from flask import (request, jsonify)
from flask_bcrypt import check_password_hash
from flask_jwt_extended import (create_access_token, jwt_required, get_jwt_identity)
from db import DB

def login():
    # Get data from request
    email = request.json.get('email', None)
    password = request.json.get('password', None)

    # Get user from database
    qry = 'SELECT * FROM `users` WHERE `email` = :email'
    user = DB.one(qry, {'email': email})

    # Check if user exists and password is correct
    if not user or not check_password_hash(user['password'], password):
        return {'message': 'invalid_credentials'}, 401
    
    # Delete password from user (should not be sent back!)
    del user['password']

    # Create JWT
    access_token = create_access_token(user)
    return jsonify(access_token =  access_token, message = 'success'),200

@jwt_required()
def me():
    user = get_jwt_identity()
    return jsonify(user=user, message='success'), 200