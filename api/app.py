from urllib import response
from flask import Flask, request, jsonify, render_template
import json
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from db import DB
from resources.user import create_user
from security import (login, me)
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

@app.route('/', methods=['GET'])
def home():
    conn = db_connection()
    if request.cookies.get('access_token'):
        print(request.cookies.get('access_token'))
   
        
    if request.method == 'GET':
        qry = 'SELECT * FROM users WHERE user_role_id = 2'
        users = DB.all(qry)
    if users is not None:
     for user in users:
       user['photo'] = base64.b64encode(user['photo']).decode('ascii')
       
       
       
    return render_template("home.html", users=users)

@app.route('/login', methods=['GET'])
def loginP():
    return render_template("login.html")
@app.route('/register', methods=['GET'])
def register():
    return render_template("register.html")
@app.route('/index', methods=['GET'])
def index():
    return render_template("index.html")
    


app.add_url_rule('/home', None, home, methods=['GET'])
app.add_url_rule('/', None, home, methods=['GET'])
# Start app
if __name__ == '__main__':
    DB.create()
    app.run(debug=True)