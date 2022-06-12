from dis import dis
from urllib import response
from flask import Flask, redirect, make_response, request, jsonify, render_template, Response, abort, url_for
import json
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from datetime import datetime, timedelta, date

from db import DB
from resources.get_color import get_color
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


@ app.route('/reservations/<int:reservation_id>/edit', methods=['POST'])
def update_reservation(reservation_id):
    try:
        me()  # check if logged in

        now = datetime.now()
        now = str(now).split('.')[0]

        req = request.form.to_dict()
        req["reservation_id"] = reservation_id
        req["now"] = now

        print(req)

        qry = '''
            UPDATE reservations
            SET date_of_reservation = :now,
                reservation_date = :start_date,
                cars_id = :car_id,
                pick_up = :pickup,
                address = :address
            WHERE id = :reservation_id
            '''

        DB.update(qry, req)

        print('reservatie geupdate van id: ' + str(reservation_id))
        return redirect(url_for('home'), code=301)
    except Exception as error:
        return {'error': str(error)}, 400


@ app.route('/cars/<int:car_id>/options', methods=['PATCH'])
def update_car_options(car_id):
    try:
        logged = me()

        if logged['user_role_id'] != 2:
            return abort(403)
        else:
            req = request.form.to_dict()
            optionsString = ""

            for key in req:
                optionsString += req[key] + ", "

            size = len(optionsString)
            slicedOptions = ""

            if(size > 0):
                slicedOptions = optionsString[:size - 2]

            req["slicedOptions"] = slicedOptions
            req["car_id"] = car_id

            qry = '''
            UPDATE cars
                SET options = :slicedOptions
                WHERE id = :car_id
            '''

            DB.update(qry, req)

            print('auto opties geupdate van ' + str(car_id))
            return redirect(url_for('home'), code=301)
    except Exception as error:
        return {'error': str(error)}, 400


@ app.route('/cars/<int:car_id>', methods=['PUT'])
def update_car(car_id):
    try:
        logged = me()

        if logged['user_role_id'] != 2:
            return abort(403)
        else:
            png = request.files["picture"]
            req = request.form.to_dict()
            req["picture"] = png.read()

            qry = '''
                UPDATE cars
                SET name = :name,
                    type_id = :type_id,
                    pickup_location_id = :pickup_location_id,
                    brand_id = :brand_id,
                    avaliability = :avaliability,
                    capacity = :capacity,
                    color = :color,
                    horsepower = :horsepower,
                    top_speed = :top_speed,
                    value = :value,
                    photo = :picture,
                    year = :year
                WHERE id = :car_id
            '''

            DB.update(qry, req)

            print('auto geupdate van' + str(car_id))
            return redirect(url_for('cars'), code=301)
    except Exception as error:
        return {'error': str(error)}, 400


@app.route('/car/<int:car_id>', methods=['DELETE'])
def delCar(car_id):
    try:
        qry = '''DELETE FROM cars WHERE '''
        return str(car_id)
    except Exception as error:
        return {'error': str(error)}, 400


@app.route('/reservations/<int:reservation_id>', methods=['GET'])
def reservationID(reservation_id):
    try:
        logged = me()
        qry = ''' SELECT  cars.photo, users.photo AS user_photo, reservations.id as reservation_id, first_name,
        last_name, customer_id, reservation_date, date_of_reservation, cars.id AS car_id,  year, color,
        cars.name as car_name, type.name as type_name FROM reservations LEFT JOIN cars on cars.id
        = reservations.cars_id LEFT JOIN type ON type.id = cars.type_id LEFT JOIN users on
            customer_id = users.id WHERE reservations.id = :reservation_id'''

        reservation = DB.one(qry, {"reservation_id": reservation_id})
        car_id = reservation['car_id']
        print(car_id, "car_id")
        qryB = '''SELECT link, cars.id, cars.name as car_name, cars.type_id as car_type_id, locations.id as location_id, brand_id, capacity, color, horsepower, top_speed, value, photo, year, locations.name as location_name, cities.id as city_id, cities.name as city_name, code, manufacturer.name as brand_name, origin from cars LEFT JOIN locations ON cars.pickup_location_id  = locations.id
                LEFT JOIN cities ON locations.cities_id = cities.id
                LEFT JOIN manufacturer on cars.brand_id = manufacturer.id
                WHERE cars.id = :car_id'''

        car = DB.one(qryB, {'car_id': car_id})
        qryC = '''SELECT * FROM cars WHERE avaliability > 0'''
        cars1 = DB.all(qryC)
        disabled = DB.all(
            'SELECT reservation_date FROM reservations WHERE cars_id = :car_id AND reservation_date > DATE()', {"car_id": car_id})

        disabledDays = []
        disabledDaysd = {}
        today = date.today() + timedelta(days=1)
        end_date = date.today() + timedelta(days=41)
        dates = {'today': today, 'max': end_date}
        for disabled in disabled:
            print("asdasdasd", disabled, "Dasdasdasdasdasdads")
            disabledDays.append(disabled['reservation_date'].split(' ')[0])
        reservationDates = DB.all(
            'SELECT reservation_date, reservations.id, cars_id FROM reservations WHERE reservation_date > DATE() GROUP BY cars_id, reservation_date')
        car_date = {}

        for reservationDate in reservationDates:
            print(" ")
            temp = []
            tempID = 0
            for cars in reservationDates:
                if cars['cars_id'] == reservationDate['cars_id']:
                    temp.append(cars['reservation_date'].split(' ')[0])
                    # print(cars['cars_id'], cars)
                    car_date[f"cars{cars['cars_id']}"] = temp
        print(car_date)

        carIds = DB.all('SELECT id FROM cars')
        ids = []
        for carId in carIds:

            ids.append(f"cars{carId['id']}")

        print(ids)

        # rows = reservationDates
        # dates = []
        # carIds = []
        # usedIds = []

        # for row in rows:
        #     tempId = 0

        #     if  row["cars_id"] not in usedIds:
        #         usedIds.append(row["cars_id"])
        #         dateRow = []
        #         count = 0

        #         for r in rows:
        #             count = count+1

        #             if tempId == r["cars_id"]:
        #                 dateRow.append(r["reservation_date"])

        #             if tempId == 0:
        #                 tempId = r["cars_id"]
        #                 dateRow.append(r["reservation_date"])
        #             # print("Count: " + str(count) + ", rows lengte: " + str(len(rows)))
        #             if count == len(rows):
        #                 dates.append(dateRow)
        #                 carIds.append(r["cars_id"])
        #                 tempId = 0
        # print(carIds, dates)

        # string = ""
        # for reservationDates in reservationDates:
        #     string = string + str(reservationDates)

        #     print(reservationDates)
        #     disabledDaysd[f"car{reservationDates['cars_id']}"] = reservationDates['reservation_date'].split(' ')[0]
        # print(string, "sdsd")
        # string = string.split("{")
        # print(str(string))

        car['photo'] = base64.b64encode(
            car['photo']).decode('ascii')
        reservation['user_photo'] = base64.b64encode(
            reservation['user_photo']).decode('ascii')
        reservation['photo'] = base64.b64encode(
            reservation['photo']).decode('ascii')
        print(cars, "cars")
        return render_template('reservation.html', reservation=reservation, ids=ids, car_date=car_date, reservationDates=disabledDaysd, dates=dates, logged=logged, cars=cars1, car=car, disabledDays=disabledDays)
        # return jsonify(reservation)
    except Exception as error:
        return {'error': str(error)}, 400


@app.route('/cars/<int:car_id>', methods=['GET', 'PATCH'])
def carsID(car_id):
    try:
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
    except Exception as error:
        return {'error': str(error)}, 400


@app.route('/reserve/<int:car_id>', methods=['GET'])
def reserveID(car_id):
    try:
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
        reservationDates = DB.all(
            'SELECT reservation_date, reservations.id, cars_id FROM reservations WHERE reservation_date > DATE() GROUP BY cars_id, reservation_date')

        disabledDays = []
        for reservation in reservations:

            disabledDays.append(reservation['reservation_date'].split(' ')[0])

        print(disabledDays)
        today = date.today() + timedelta(days=1)
        end_date = date.today() + timedelta(days=41)
        dates = {'today': today, 'max': end_date}

        car['photo'] = base64.b64encode(car['photo']).decode('ascii')
        return render_template("carReserve.html", dates=dates, logged=logged, reservationDates=reservationDates, disabledDays=disabledDays, car=car)
    except Exception as error:
        return {'error': str(error)}, 400


@app.route('/reservations/<int:reservation_id>/changes', methods=['POST'])
def reservationsChanges(reservation_id):
    try:
        logged = {}
        logged = me()
        today = datetime.now()
        today = str(today).split('.')[0]
        print(today, "yesh")

        args = request.form.to_dict()
        # check if args has del
        if 'del' in args:

            qry = '''UPDATE reservations SET visibility = 0, time_of_deletion = :time_of_deletion WHERE id = :reservation_id'''
            DB.update(qry, {"time_of_deletion": today,
                            "reservation_id": reservation_id})
            return redirect(url_for('home')), 301
    except Exception as error:
        return {'error': str(error)}, 400


@app.route('/reservations/<int:car_id>', methods=['POST'])
def reservations(car_id):
    try:
        logged = {}
        logged = me()

        today = datetime.now()
        today = str(today).split('.')[0]
        print(today)
        dates = request.form.to_dict()
        if 'date_of_reservation' in dates:
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
                    (`customer_id`, `cars_id`, `reservation_date`, `date_of_reservation`, `pick_up`, `address`)
                VALUES
                    (:customer_id, :cars_id, :reservation_date, :date_of_reservation, :pick_up, :address)
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
    except Exception as error:
        return {'error': str(error)}, 400


# Start app
if __name__ == '__main__':
    DB.create()
    app.run(debug=True)

app.add_url_rule('/log-out', None, logout, methods=['GET'])
