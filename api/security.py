from math import exp
from flask import request, jsonify, make_response, render_template, redirect, url_for, abort
from flask_bcrypt import check_password_hash
from flask_jwt_extended import (create_access_token, jwt_required, get_jwt_identity)
from datetime import datetime, timedelta
from db import DB
import jwt
def login():
    # Get data from request
    args = request.form.to_dict()
    email = args['email']
    password = args['password']
    print(email, password, "yes")
    # Get user from database
    qry = 'SELECT * FROM `users` WHERE `email` = :email'
    user = DB.one(qry, {'email': email})
    if not user:
        return abort(403)
    del user['photo']
    print(user)
    # Check if user exists and password is correct
    if not user or not check_password_hash(user['password'], password):
        return {'message': 'invalid_credentials'}, 401
    
    # Delete password from user (should not be sent back!)
    del user['password']

    # Create JWT
    dt = datetime.now() + timedelta(days=2)
    user['exp'] = dt
    print(user, "yeeeeee        ")
    access_token = jwt.encode(user, 'qominiqueisshitinoverwatch', algorithm='HS256')
    resp = make_response(redirect('/'))
    resp.set_cookie('access_token', access_token, expires="never")
    return resp, 200


def me():
    if not request.cookies.get('access_token'):
        return abort(401)
        
    user = jwt.decode(request.cookies.get('access_token'), 'qominiqueisshitinoverwatch', algorithms=["HS256"])
    print(user)
    return user

def logout():
    logged = me()
    print("dasdasd")
    resp = make_response(redirect(url_for('home')))
    resp.set_cookie("access_token", '', expires=0)
    return resp, 200