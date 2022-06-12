from flask import request, redirect, url_for
from flask_bcrypt import generate_password_hash
from db import DB
from werkzeug.utils import secure_filename


def create_user():
    try:
        # Parse all arguments for validity

        picture = request.files["picture"]

        args = request.form.to_dict()

        args["picture"] = picture.read()
        qry = '''
        INSERT INTO 
            `users` 
                (`email`, `password`, `first_name`, `last_name`, `phone_number`, `user_role_id`, `photo`)
            VALUES
                (:email, :password, :first_name, :last_name, :phonenumber, 1, :picture)
        '''

        # Hash the password before inserting
        args['password'] = generate_password_hash(args['password'])

        # Insert the user into the database
        id = DB.insert(qry, args)

        # Return a message and the user id
        return redirect(url_for('home')), 301
    except Exception as error:
        print(f'Error: {error}')
