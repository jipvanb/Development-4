from urllib import response
from flask import Flask, redirect, make_response, request, jsonify, render_template, Response, abort, url_for
import json
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from datetime import datetime, timedelta, date

from db import DB
from resources.user import create_user
from resources.routes import (
    home, register, loginP, cars, addCars, reserve, allreservations, reservationsU)
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
# app.add_url_rule('/logout', None, logoutt, methods=['GET'])
app.add_url_rule('/login', None, loginP, methods=['GET'])
app.add_url_rule('/cars', None, cars, methods=['GET'])
app.add_url_rule('/reserve', None, reserve, methods=['GET'])
app.add_url_rule('/addCar', None, addCars, methods=['GET', 'POST'])
app.add_url_rule('/allreservations', None, allreservations, methods=['GET'])
app.add_url_rule('/reservations', None, reservationsU, methods=['GET'])


@app.route('/car/<int:car_id>', methods=['DELETE'])
def delCar(car_id):
    qry = '''DELETE FROM cars WHERE '''
    return str(car_id)


@app.route('/reservations/<int:reservation_id>', methods=['GET'])
def reservationID(reservation_id):
    logged = me()
    qry = ''' SELECT  cars.photo, users.photo AS user_photo, reservations.id as reservation_id, first_name,
     last_name, customer_id, reservation_date, date_of_reservation, cars.id AS car_id,  year, color,
      cars.name as car_name, type.name as type_name FROM reservations LEFT JOIN cars on cars.id
       = reservations.cars_id LEFT JOIN type ON type.id = cars.type_id LEFT JOIN users on
        customer_id = users.id WHERE reservations.id = :reservation_id'''
    reservation = DB.one(qry, {"reservation_id": reservation_id})

    reservation['user_photo'] = base64.b64encode(
        reservation['user_photo']).decode('ascii')
    reservation['photo'] = base64.b64encode(
        reservation['photo']).decode('ascii')
    return render_template('reservation.html', reservation=reservation, logged=logged)
    # return jsonify(reservation)


@app.route('/cars/<int:car_id>', methods=['GET', 'PATCH'])
def carsID(car_id):
    logged = {}
    if not request.cookies.get('access_token'):
        return abort(401)

    else:
        conn = db_connection()
        logged = me()
        if logged['user_role_id'] != 2:
            return abort(403)
    if request.method == "GET":

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
    if request.method == 'PATCH':
        qry = ''' UPDATE cars
        SET avaliability = :avaliability,
            deletion_date = :deletion_date
        WHERE id = :carId               
        '''
        DB.update(qry, {"carId": car_id, "avaliability": 0,
                  "deletion_date": date.today()})
        return str(car_id)


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
    reservations = DB.all(
        'SELECT reservation_date FROM reservations WHERE cars_id = :car_id AND reservation_date > DATE()', {"car_id": car_id})
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


@app.route('/reservations/<int:reservation_id>/changes', methods=['POST'])
def reservationsChanges(reservation_id):
    logged = {}
    logged = me()
    today = datetime.now()
    today = str(today).split('.')[0]
    print(today, "yesh")

    args = request.form.to_dict()
    # check if args has del
    if 'del' in args:
        
        qry = '''UPDATE reservations SET visibility = 0, time_of_deletion = :time_of_deletion WHERE id = :reservation_id'''
        DB.update(qry, {"time_of_deletion":today ,"reservation_id": reservation_id})
        return redirect(url_for('home')), 301


@app.route('/reservations/<int:car_id>', methods=['POST'])
def reservations(car_id):
    logged = {}
    logged = me()
    
    today = datetime.now()
    today = str(today).split('.')[0]
    print(today)
    dates = request.form.to_dict()
    if 'start_date' in dates:
        # give default value to pickup unless value is given
        if 'pickup' not in dates:
            pickup = 0

        else:
            pickup = 1

        if 'address' not in dates:
            address = 0

        else:
            address = dates['address']

        args = {'cars_id': str(car_id), 'customer_id': logged['id'], 'reservation_date': dates['start_date'],
                'date_of_reservation': today, 'pick_up': pickup, 'address': address}
        qry = '''
        
        INSERT INTO 
            `reservations` 
                (`customer_id`, `cars_id`, `reservation_date`, `date_of_reservation`, `pick_up`, `address`, `visibility`)
            VALUES
                (:customer_id, :cars_id, :reservation_date, :date_of_reservation, :pick_up, :address, 1)
        '''

        DB.insert(qry, args)

        resp = make_response(redirect('/'))
        return resp, 201
    else:
        print(dates)
        reservation_id = car_id
        # update reservation visibility with 1 and time of deletion with null
        qry = '''UPDATE reservations SET visibility = 1, time_of_deletion = NULL WHERE id = :reservation_id'''
        DB.update(qry, {"reservation_id": reservation_id})
        resp = make_response(redirect('/'))
        return resp, 201

# Start app
if __name__ == '__main__':
    DB.create()
    app.run(debug=True)

app.add_url_rule('/log-out', None, logout, methods=['GET'])