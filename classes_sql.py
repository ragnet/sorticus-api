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
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, Boolean, String, Float

Base = declarative_base()

class Product(Base):
    __tablename__ = "product"

    barcode = Column(String, primary_key=True)
    product_seq = Column(Integer, primary_key=True)    
    product_name = Column(String)	   
    category = Column(String)	    
    mat_refund_id = Column(Integer)

class Stores(Base):
    __tablename__ = "stores"

    store_id = Column(Integer, primary_key=True)
    postal_code = Column(String, primary_key=True)	
    address = Column(String)
    city = Column(String)	
    province = Column(String)
    lat = Column(Float)
    lon = Column(Float)
    recyc_id = Column(Integer)

class Store_refund(Base):
    __tablename__ = "store_refund"

    store_recyc_id = Column(Integer, primary_key=True)
    mat_refund_id = Column(Integer, primary_key=True)    
    prod_receive = Column(Boolean)	
    prod_pay = Column(Boolean)    

class Store_name(Base):
    __tablename__ = "store_name"

    store_id = Column(Integer, primary_key=True)
    store_name = Column(String)        

class Store_type(Base):
    __tablename__ = "store_type"

    store_recyc_id = Column(Integer, primary_key=True)  
    store_type_desc = Column(String)

class Refundable(Base):
    __tablename__ = "refundable"

    mat_refund_id = Column(Integer, primary_key=True)  
    mat_name = Column(String)
    mat_vol_desc = Column(String)  
    mat_refund_value = Column(Float)      

