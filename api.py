import json
import mysql.connector
from flask import Flask, jsonify

# TODO: This configuration should be moved to an environment file
cnx = mysql.connector.connect(user='', 
                              password='',
                              host='127.0.0.1',
                              database='demo')

app = Flask(__name__)

#
# Routes
# GET /places
#
@app.route('/places', methods=['GET'])
def get_places():
    try:
        cursor = cnx.cursor()
        cursor.execute("SELECT * FROM places")
        places = cursor.fetchall()

        return jsonify(places)
    except Exception as e:
        return jsonify({'error': str(e)})
    finally:
        cursor.close()

@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({'status': 'ok'})

#
# Run the api server
#
if __name__ == '__main__':
    app.run(debug=True, port=5000)