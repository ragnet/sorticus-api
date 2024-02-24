""" 
*-----------------------------------------------------------------*
* Sorticus Innovation inc.                                        *
* -----------------------                                         *
*                                                                 *
* RECYCICI APP                                                    *
*                                                                 *
* Developed by: Fernanda Custodio Pereira do Carmo                *
* Template by: Rogerio Golcalves (Ragnet)                         *
*                                                                 *
* February/2024                                                   *
*                                                                 *
*-----------------------------------------------------------------*
"""

from flask import Flask, jsonify, request
from sqlalchemy import create_engine, select, and_, func
from classes_sql import Product, Stores, Store_refund, Store_name, Store_type, Refundable
from dotenv import load_dotenv
import os
import cv2
import random

load_dotenv()

API_SECRET = os.getenv('API_SECRET')

host=os.getenv('MYSQL_HOST')
user=os.getenv('MYSQL_USER')
password=os.getenv('MYSQL_PASSWORD')
database=os.getenv('MYSQL_DATABASE')
port=os.getenv('MYSQL_PORT')

dist=200
path_s3 = "/home/ec2-user/service/api/images/"
unique_figure_id = "WIN_20231219_14_03_50_Pro"
max_result=3
max_result_all=500

app = Flask(__name__)

def get_db_connection():
    return create_engine(url="mysql+pymysql://{0}:{1}@{2}:{3}/{4}".format(user, password, host, port, database))

def check_secret():
    if request.headers.get('X-Api-Secret') != API_SECRET:
        raise Exception('Invalid API secret')

@app.route('/get_material/<barcode_user>', methods=['GET'])
async def get_material(barcode_user):
    try:
        #check_secret()
        engine = get_db_connection()
    
        stmt = select(Product.mat_refund_id, 
                        Refundable.mat_name,
                        Refundable.mat_refund_value). \
                where(and_
                        (Product.barcode==barcode_user, 
                        Product.product_seq==0)). \
                        join(Refundable, Product.mat_refund_id==Refundable.mat_refund_id)
        
        row = engine.connect().execute(stmt).first()    
        
        if row is None:
            msg = "barcode not found"
            return jsonify({'error': msg}), 401  
        else:
            result = {'material_id' : row[0], 
                            'material_name' : row[1], 
                            'refund_value' : row[2]}
            return(dict(result))

    except Exception as e:
        return jsonify({'error': str(e)}), 401

@app.route('/obtain_barcode/<figure_id>', methods=['GET'])
async def obtain_barcode(figure_id):
    #check_secret()    
    
    try:
        img = cv2.imread(path_s3 + figure_id + ".jpg")
        bd = cv2.barcode.BarcodeDetector()
        barcode, _1, _2 = bd.detectAndDecode(img)    
    except Exception as e:
        return jsonify({'error': str(e)}), 401              
    
    result = {'barcode_user' : barcode}
    return(dict(result))          

@app.route('/get_location', methods=['GET'])
async def get_location():
    result = {'lat_user' : 45.527027 + random.uniform(-1, 1), 
              'lon_user' : -73.715532 + random.uniform(-1, 1)}
    return(dict(result))         

@app.route('/get_material_store', methods=['GET'])    
async def get_material_store():
    dict_barcode = await obtain_barcode(unique_figure_id)     

    barcode = int(dict_barcode.get("barcode_user"))
    dict_material = await get_material(barcode)

    mat_id = int(dict_material.get("material_id"))

    dict_lat_lon = await get_location()    
    lat_user=dict_lat_lon.get("lat_user")
    lon_user=dict_lat_lon.get("lon_user")

    dict_store = await get_store(lat_user, lon_user, mat_id)

    res_dict_store = {"store_" + str(i): dict_store[i] for i in range(len(dict_store))}

    return(dict_barcode | dict_lat_lon |  dict_material | res_dict_store)
                   
@app.route('/get_store/<lat_user>&<lon_user>&<mat_id>', methods=['GET'])    
async def get_store(lat_user, lon_user, mat_id):

    try:
        #check_secret()
        engine = get_db_connection()

        distance = (6371 * func.acos (func.cos ( func.radians(lat_user) )
                    * func.cos( func.radians( Stores.lat ) )
                    * func.cos( func.radians( Stores.lon ) - func.radians(lon_user) )
                    + func.sin ( func.radians(lat_user) )
                    * func.sin( func.radians( Stores.lat ) ) )).label("distance")
                             
        stmt = select(Store_name.store_name, 
                        Stores.address, 
                        Stores.city, 
                        Stores.postal_code, 
                        Stores.lat, 
                        Stores.lon,
                        distance). \
                where(and_(Stores.recyc_id.in_(select(Store_refund.store_recyc_id).where(and_(Store_refund.mat_refund_id == mat_id, Store_refund.prod_pay == 1))), 
                            distance<dist)). \
                        order_by(distance). \
                        limit(max_result). \
                        join(Store_name, Store_name.store_id==Stores.store_id)     

        rows = engine.connect().execute(stmt)
        result=[]

        if rows is None:
            msg = "store not found for this material"
            return jsonify({'error': msg}), 401            
        else:        
            for row in rows:
                result.append({'estab' : row[0], 
                            'address' : row[1], 
                            'city' : row[2],  
                            'postal_code' : row[3],
                            'lat' : row[4],
                            'lon' : row[5],
                            'dist' : row[6]})
            return(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 401
                   
@app.route('/get_store_desc/<store_id>&<postal_code>', methods=['GET'])    
async def get_store_desc(store_id, postal_code):

    try:
        #check_secret()
        engine = get_db_connection()

        stmt = select(Store_type.store_type_desc). \
                select_from(Stores). \
                where(and_(Stores.store_id==store_id), (Stores.postal_code==postal_code)). \
                        join(Store_type, Store_type.store_recyc_id==Stores.recyc_id). \
                        join(Store_name, Stores.store_id == Store_name.store_id)                     

        row = engine.connect().execute(stmt).first()

        if row is None:
            msg = "Store type description not found"
            return jsonify({'error': msg}), 401            
        else:        
            result = row[0] 
            return(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 401
    
@app.route('/get_store_all/<lat_user>&<lon_user>', methods=['GET'])    
async def get_store_all(lat_user, lon_user):

    try:
        #check_secret()
        engine = get_db_connection()

        distance = (6371 * func.acos (func.cos ( func.radians(lat_user) )
                    * func.cos( func.radians( Stores.lat ) )
                    * func.cos( func.radians( Stores.lon ) - func.radians(lon_user) )
                    + func.sin ( func.radians(lat_user) )
                    * func.sin( func.radians( Stores.lat ) ) )).label("distance")

        stmt = select(Store_name.store_name, 
                        Stores.address, 
                        Stores.city, 
                        Stores.postal_code, 
                        Stores.lat, 
                        Stores.lon,
                        distance,
                        Stores.store_id,
                        Stores.postal_code). \
                where(distance<dist). \
                        order_by(distance). \
                        limit(max_result_all). \
                        join(Store_name, Store_name.store_id==Stores.store_id)                         

        rows = engine.connect().execute(stmt)
        result=[]

        if rows is None:
            msg = "store not found for this material"
            return jsonify({'error': msg}), 401            
        else:        
            for row in rows:
                store_type_desc = await get_store_desc(row[7], row[8])  
                result.append({'estab' : row[0], 
                            'address' : row[1], 
                            'city' : row[2],  
                            'postal_code' : row[3],
                            'lat' : row[4],
                            'lon' : row[5],
                            'dist' : row[6],
                            'store_type_desc': store_type_desc})
            return(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 401

@app.route('/ping', methods=['GET', 'POST'])
def ping():
    try:
        return jsonify({'status': 'ok'})
    except Exception as e:
        return jsonify({'error': str(e)}), 401

#
# Run the api server
#
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)
