import os
import mysql.connector

from dotenv import load_dotenv
from flask import Flask, request, jsonify

load_dotenv()

API_SECRET = os.getenv('API_SECRET')

app = Flask(__name__)

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_DATABASE')
    )

def check_secret():
    if request.headers.get('X-Api-Secret') != API_SECRET:
        raise Exception('Invalid API secret')

#
# Routes
#
# GET /places
#
@app.route('/places', methods=['GET'])
def get_places():
    try:
        check_secret()

        cnx = get_db_connection()
        cursor = cnx.cursor()
        cursor.execute("SELECT * FROM places")
        places = cursor.fetchall()

        return jsonify(places)
    except Exception as e:
        return jsonify({'error': str(e)}), 401
    finally:
        cursor.close()

#
# GET /ping
#
@app.route('/ping', methods=['GET', 'POST'])
def ping():
    try:
        check_secret()

        return jsonify({'status': 'ok'})
    except Exception as e:
        return jsonify({'error': str(e)}), 401

#
# Run the api server
#
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)