from flask import Flask, request, redirect, jsonify, make_response, render_template, abort
from security import (login, me, logout)
from db import DB
import sqlite3
import base64
from datetime import datetime, timedelta, date


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
    
    avaliability = ''' UPDATE cars
    SET avaliability = :avaliability
    WHERE id = :carId               
    '''
    for car in car_ids:
        
        if car['reservation_date'] == today_date:
            print(car['reservation_date'], "is today")
            DB.update(avaliability,{"carId":car['cars_id'], "avaliability":0})
        else:
            DB.update(avaliability,{"carId":car['cars_id'], "avaliability":1})
            print(car['reservation_date'], "is in the past")
    
    qry = '''SELECT cars.id, photo, year, color, cars.name as car_name, type.name as type_name FROM cars LEFT JOIN type ON type.id = cars.type_id WHERE avaliability > 0 '''
    cars = DB.all(qry)
    for car in cars:
        car['photo'] = base64.b64encode(car['photo']).decode('ascii')
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
        qry = '''INSERT INTO 
        `cars` 
            (`name`, `type_id`, `pickup_location_id`, `brand_id`, `avaliability`, `capacity`, `color`, `horsepower`, `top_speed`, `value`, `photo`, `year`)
        VALUES
            (:name, :type_id, :pickup_location_id, :brand_id, :avaliability, :capacity, :color, :horsepower, :top_speed, :value, :photo, :year)'''
        types = DB.insert(qry, args)
        resp = make_response(redirect('/cars'))
        return resp, 201
