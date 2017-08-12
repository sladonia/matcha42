#!/usr/bin/env python

# A very simple Flask Hello World app for you to get started with...

# from flask import Flask

# app = Flask(__name__)

# @app.route('/')
# def hello_world():
#     return 'Hello from Flask!'

import app
from config import production_config as config
#from config import developer_config as config
from flask_sslify import SSLify

app = app.init_app(config)
sslify = SSLify(app)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
