from urllib import response
from flask import Flask, request, jsonify, render_template
import json
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from db import DB
from resources.user import create_user
from resources.routes import (home, register, loginP)
from security import (login, me, logout)
import sqlite3 
import base64
from flask_jwt_extended import (create_access_token, jwt_required, get_jwt_identity, verify_jwt_in_request)
# Create a new Flask application

app = Flask(__name__)
app.debug = True
def db_connection():
    conn = None
    try:
        conn = sqlite3.connect("car_rental.db")
    except sqlite3.error as e:
            print(e)
    return conn
# Enable cors on the server
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://img.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

CORS(app)

# Register the JWT manager
app.config['JWT_SECRET_KEY'] = 'qominiqueisshitinoverwatch'
jwt = JWTManager(app)

# ============================ Routes ============================

# JWT routes
app.add_url_rule('/users', None, create_user, methods=['POST'])
app.add_url_rule('/auth', None, login, methods=['POST'])
app.add_url_rule('/me', None, me, methods=['GET'])
app.add_url_rule('/', None, home, methods=['GET'])
app.add_url_rule('/register', None, register, methods=['GET'])
app.add_url_rule('/logout', None, logout, methods=['GET'])
app.add_url_rule('/login', None, loginP, methods=['GET'])
# Start app   
if __name__ == '__main__':
    DB.create()
    app.run(debug=True)