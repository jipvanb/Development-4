from flask import Flask, request, redirect, jsonify, make_response, render_template, abort
from security import (login, me, logout)
from db import DB
import sqlite3
import base64
from datetime import datetime, timedelta, date
import json


def db_connection():
    conn = None
    try:
        conn = sqlite3.connect("car_rental.db")
    except sqlite3.error as e:
        print(e)
    return conn


def home():
    conn = db_connection()
    logged = {}
    reservations = {}

    if request.cookies.get('access_token'):
        print(request.cookies.get('access_token'))
        logged = me()
        print(logged)

        print(logged['id'], "me")
        args = {"id": logged['id']}
        qryR = ''' SELECT  photo, customer_id, reservation_date, date_of_reservation, cars.id,  year, color, cars.name as car_name, type.name as type_name FROM reservations LEFT JOIN cars on cars.id = reservations.cars_id LEFT JOIN type ON type.id = cars.type_id WHERE customer_id = :id'''
        reservations = DB.all(qryR, args)
        for reservation in reservations:
            reservation['photo'] = base64.b64encode(
                reservation['photo']).decode('ascii')

    if request.method == 'GET':
        qry = 'SELECT * FROM users WHERE user_role_id = 2'
        users = DB.all(qry)
    if users is not None:
        for user in users:
            user['photo'] = base64.b64encode(user['photo']).decode('ascii')

    return render_template("home.html", logged=logged, users=users, reservations=reservations)


def register():
    return render_template("register.html")


def loginP():
    return render_template("login.html")


def cars():
    logged = {}
    if not request.cookies.get('access_token'):
        return abort(401)

    else:
        conn = db_connection()
        logged = me()
        if logged['user_role_id'] != 2:
            return abort(403)
    print(logged)

    qry = '''SELECT cars.id, photo, year, color, cars.name as car_name, type.name as type_name FROM cars LEFT JOIN type ON type.id = cars.type_id'''
    cars = DB.all(qry)
    for car in cars:
        car['photo'] = base64.b64encode(car['photo']).decode('ascii')
    return render_template("cars.html", logged=logged, cars=cars)


def reserve():
    logged = {}
    if request.cookies.get('access_token'):
        conn = db_connection()
        logged = me()
    print(logged)
    today = datetime.now()
    qryA = '''SELECT MAX(reservation_date) AS reservation_date, cars_id FROM reservations WHERE reservation_date <= DATE() GROUP BY cars_id'''
    car_ids = DB.all(qryA)
    print(car_ids)
    print(date.today(), "todayyy")
    today_date = date.today()
    today_date = str(today_date)

    
    deletions = DB.all(qryb)
    print(today_date, "dasdasdasd")
    for deletion in deletions:
        if deletion['deletion_date']:
            if deletion['deletion_date'] <= today_date:
                qry = '''DELETE FROM cars WHERE :car_id'''
                DB.delete(qry, {"car_id":deletion['id']})
                print(deletion, "deleted")
    # avaliability = ''' UPDATE cars
    # SET avaliability = :avaliability
    # WHERE id = :carId               
    # '''
    # for car in car_ids:

    #     if car['reservation_date'] == today_date:
    #         print(car['reservation_date'], "is today")
    #         DB.update(avaliability, {
    #                   "carId": car['cars_id'], "avaliability": 0})
    #     else:
    #         DB.update(avaliability, {
    #                   "carId": car['cars_id'], "avaliability": 1})
    #         print(car['reservation_date'], "is in the past")

    qry = '''SELECT cars.id, photo, year, color, cars.name as car_name, type.name as type_name FROM cars LEFT JOIN type ON type.id = cars.type_id WHERE starting_date <= DATE() AND avaliability > 0'''
    cars = DB.all(qry)
    # for car in cars:
    #     car['photo'] = base64.b64encode(car['photo']).decode('ascii')
    return render_template("reserve.html", logged=logged, cars=cars)


def addCars():

    logged = {}
    conn = db_connection()
    if request.method == 'GET':
        qry = '''SELECT * FROM type'''
        types = DB.all(qry)
        qryN = '''SELECT * FROM manufacturer'''
        brands = DB.all(qryN)
        qryL = '''SELECT locations.name as location_name, locations.id as location_id, cities.name as city_name  FROM locations LEFT JOIN cities on cities.id = locations.cities_id'''
        locations = DB.all(qryL)
        return render_template("addCar.html", locations=locations, brands=brands, types=types, logged=logged)
    if request.method == 'POST':
        photo = request.files["photo"]
        args = request.form.to_dict()
        args["photo"] = photo.read()
        args["type_id"] = args["type_id"].split(' ')[0]
        args["brand_id"] = args["brand_id"].split(' ')[0]
        args["pickup_location_id"] = args["pickup_location_id"].split(' ')[0]
        args["avaliability"] = 1
        args["starting_date"] = "-"
        args["deletion_date"] = "-"
        qry = '''INSERT INTO 
        `cars` 
            (`name`, `type_id`, `pickup_location_id`, `brand_id`, `avaliability`, `capacity`, `color`, `horsepower`, `top_speed`, `value`, `photo`, `year`, `starting_date`, `deletion_date`)
        VALUES
            (:name, :type_id, :pickup_location_id, :brand_id, :avaliability, :capacity, :color, :horsepower, :top_speed, :value, :photo, :year, :starting_date, :deletion_date)'''
        DB.insert(qry, args)
        resp = make_response(redirect('/cars'))
        return resp, 201


def allreservations():
    logged = {}
    if not request.cookies.get('access_token'):
        return abort(401)

    else:
        conn = db_connection()
        logged = me()
        if logged['user_role_id'] != 2:
            return abort(403)
    print(logged)
    qry2 = '''SELECT id, name from cars'''
    ids = DB.all(qry2)
    qry = ''' SELECT  cars.photo, users.photo AS user_photo, reservations.id as reservation_id, first_name, last_name, customer_id, reservation_date, date_of_reservation, cars.id AS car_id,  year, color, cars.name as car_name, type.name as type_name FROM reservations LEFT JOIN cars on cars.id = reservations.cars_id LEFT JOIN type ON type.id = cars.type_id LEFT JOIN users on customer_id = users.id'''
    cars = DB.all(qry)

    # for idss in ids:
    #     print(idss['id'], "id", idss['name'])

    #     cars.append({"car": DB.all(qry, {"car_id": idss['id']})})
    #     bam = []
    # i = 0
    # for count, value in enumerate(ids):

    #     for count, value in enumerate(cars[i]['car']):
    #         print(count, value['reservation_id'], "reservation_id")
    #     print(i, 'i')
    #     i = i+1

    for car in cars:
        car['user_photo'] = base64.b64encode(car['user_photo']).decode('ascii')
        car['photo'] = base64.b64encode(car['photo']).decode('ascii')
    return render_template('reservations.html', logged=logged, ids=ids, i=0, cars=cars)
    # return json.dumps(cars[1]['car'])
