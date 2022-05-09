from cgi import test
from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return 'Hello World! <a href="/user">user</a>'

@app.route('/user')
def user():
    return '<a>Jip van Buitenen</a>'

app.run()