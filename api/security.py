from flask import request, jsonify, make_response, render_template, redirect, url_for
from flask_bcrypt import check_password_hash
from flask_jwt_extended import (create_access_token, jwt_required, get_jwt_identity)
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
    del user['photo']
    print(user)
    # Check if user exists and password is correct
    if not user or not check_password_hash(user['password'], password):
        return {'message': 'invalid_credentials'}, 401
    
    # Delete password from user (should not be sent back!)
    del user['password']

    # Create JWT
    access_token = create_access_token(user)
    resp = make_response(redirect("/"))
    resp.set_cookie('access_token', access_token)
    return resp, 200


def me():
    user = jwt.decode(request.cookies.get('access_token'), 'qominiqueisshitinoverwatch', algorithms=["HS256"])
    return jsonify(user=user, message='success'), 200