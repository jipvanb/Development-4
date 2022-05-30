from flask import Flask, request, jsonify, render_template
from security import (login, me, logout)
from db import DB
import sqlite3 
import base64
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
        logged = logged['sub']
        print(logged['id'], "me")
        args = {"id":logged['id']}
        qryR = ''' SELECT * FROM reservations WHERE customer_id = :id'''
        reservations = DB.all(qryR, args)
        print(reservations, "reservations")
    if request.method == 'GET':
        qry = 'SELECT * FROM users WHERE user_role_id = 2'
        users = DB.all(qry)
    if users is not None:
     for user in users:
       user['photo'] = base64.b64encode(user['photo']).decode('ascii')
       
       
       
    return render_template("home.html", logged=logged, users=users)

def register():
    return render_template("register.html")

def loginP():
    return render_template("login.html")

def cars():
    logged = {}
    conn = db_connection()
    logged = me()
    logged = logged['sub']
    qry= '''SELECT * FROM cars'''
    cars = DB.all(qry)
    return render_template("cars.html", logged=logged, cars=cars)