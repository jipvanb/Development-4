from flask import request
from flask_bcrypt import generate_password_hash
from db import DB

def create_user():
    # Parse all arguments for validity
    args = request.get_json()

    # Make the insert query with parameters
    qry = '''
    INSERT INTO 
        `users` 
            (`email`, `password`, `firstname`, `lastname`)
        VALUES
            (:email, :password, :firstname, :lastname)
    '''
    
    # Hash the password before inserting
    args['password'] = generate_password_hash(args['password'])

    # Insert the user into the database
    id = DB.insert(qry, args)

    # Return a message and the user id
    return {'message': 'success', 'id': id}, 201