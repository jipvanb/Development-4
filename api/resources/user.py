from flask import request
from flask_bcrypt import generate_password_hash
from db import DB
from werkzeug.utils import secure_filename
def create_user(list):
    # Parse all arguments for validity
    args = request.get_json()
    print(list, "args")
   
    qry = '''
    INSERT INTO 
        `users` 
            (`email`, `password`, `first_name`, `last_name`, `phone_number`, `user_role_id`)
        VALUES
            (:email, :password, :first_name, :last_name, :phonenumber, 1)
    '''
    
    # Hash the password before inserting
    args['password'] = generate_password_hash(args['password'])

    # Insert the user into the database
    id = DB.insert(qry, args)

    # Return a message and the user id
    return {'message': 'success', 'id': id}, 201