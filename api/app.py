from urllib import response
from flask import Flask,redirect, make_response, request, jsonify, render_template, Response, abort
import json
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from datetime import datetime, timedelta, date

from db import DB
from resources.get_color import get_color
from resources.user import create_user
from resources.routes import (home, register, loginP, cars, addCars, reserve, allreservations)
from security import (login, me, logout)
import sqlite3
import base64
from flask_jwt_extended import (
    create_access_token, jwt_required, get_jwt_identity, verify_jwt_in_request)
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
app.add_url_rule('/cars', None, cars, methods=['GET'])
app.add_url_rule('/reserve', None, reserve, methods=['GET'])
app.add_url_rule('/addCar', None, addCars, methods=['GET', 'POST'])
app.add_url_rule('/allreservations', None, allreservations, methods=['GET'])
 




@app.route('/cars/<int:car_id>', methods=['GET'])
def carsID(car_id):
    logged = {}
    
    if not request.cookies.get('access_token'):
        return abort(401)

    else:
        conn = db_connection()
        logged = me()
        if logged['user_role_id'] != 2:
            return abort(403)
        
    
    qry = '''SELECT link, cars.id, cars.name as car_name, cars.type_id as car_type_id, locations.id as location_id, brand_id, capacity, color, horsepower, top_speed, value, photo, year, locations.name as location_name, cities.id as city_id, cities.name as city_name, code, manufacturer.name as brand_name, origin from cars LEFT JOIN locations ON cars.pickup_location_id  = locations.id
            LEFT JOIN cities ON locations.cities_id = cities.id
            LEFT JOIN manufacturer on cars.brand_id = manufacturer.id
            WHERE cars.id = :car_id'''
    print(car_id)
    args = {"car_id": car_id}
    car = DB.one(qry, {'car_id': car_id})
    today = date.today() + timedelta(days=1)
    end_date = date.today() + timedelta(days=41)
    dates = {'today': today, 'max': end_date}

    car['photo'] = base64.b64encode(car['photo']).decode('ascii')
    return render_template("car.html", dates=dates, logged=logged, car=car)

@app.route('/reserve/<int:car_id>', methods=['GET'])
def reserveID(car_id):
    logged = {}

    if request.cookies.get('access_token'):
        conn = db_connection()
        logged = me()

    conn = db_connection()
    qry = '''SELECT link, cars.id, cars.name as car_name, cars.type_id as car_type_id, locations.id as location_id, brand_id, capacity, color, horsepower, top_speed, value, photo, year, locations.name as location_name, cities.id as city_id, cities.name as city_name, code, manufacturer.name as brand_name, origin from cars LEFT JOIN locations ON cars.pickup_location_id  = locations.id
            LEFT JOIN cities ON locations.cities_id = cities.id
            LEFT JOIN manufacturer on cars.brand_id = manufacturer.id
            WHERE cars.id = :car_id'''
    print(car_id)
    args = {"car_id": car_id}
    car = DB.one(qry, {'car_id': car_id})
    reservations = DB.all('SELECT reservation_date FROM reservations WHERE cars_id = :car_id AND reservation_date > DATE()', {"car_id": car_id})
    print(reservations, "reservations")
    disabledDays = []
    for reservation in reservations:
        
        disabledDays.append(reservation['reservation_date'].split(' ')[0])
    print(disabledDays)
    today = date.today() + timedelta(days=1)
    end_date = date.today() + timedelta(days=41)
    dates = {'today': today, 'max': end_date}

    car['photo'] = base64.b64encode(car['photo']).decode('ascii')
    return render_template("carReserve.html", dates=dates, logged=logged, disabledDays=disabledDays, car=car)

@app.route('/reservations/<int:car_id>', methods=['POST'])
def reservations(car_id):
     logged = {}
     logged = me()
     today = datetime.now()
     today = str(today).split('.')[0]
     print(today)
     dates = request.form.to_dict()
     args = {'cars_id':str(car_id), 'customer_id':logged['id'], 'reservation_date':dates['start_date'], 'date_of_reservation':today}
     qry = '''
     
    INSERT INTO 
        `reservations` 
            (`customer_id`, `cars_id`, `reservation_date`, `date_of_reservation`)
        VALUES
            (:customer_id, :cars_id, :reservation_date, :date_of_reservation)
    '''
        
        
     DB.insert(qry,args)
     
     resp = make_response(redirect('/'))
     return resp, 201

# Start app
if __name__ == '__main__':
    DB.create()
    app.run(debug=True)
