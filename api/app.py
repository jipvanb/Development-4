from urllib import response
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from db import DB
from resources.user import create_user
from security import (login, me)

# Create a new Flask application
app = Flask(__name__)
app.debug = True

# Enable cors on the server
CORS(app)

# Register the JWT manager
app.config['JWT_SECRET_KEY'] = 'qominiqueisshitinoverwatch'
jwt = JWTManager(app)

# ============================ Routes ============================

# JWT routes
app.add_url_rule('/users', None, create_user, methods=['POST'])
app.add_url_rule('/auth', None, login, methods=['POST'])
app.add_url_rule('/me', None, me, methods=['GET'])

# Start app
if __name__ == '__main__':
    DB.create()
    app.run()