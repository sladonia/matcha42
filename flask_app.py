
# A very simple Flask Hello World app for you to get started with...

# from flask import Flask

# app = Flask(__name__)

# @app.route('/')
# def hello_world():
#     return 'Hello from Flask!'

import app
from config import production_config as config
from flask_sslify import SSLify

app = app.init_app(config)
sslify = SSLify(app)