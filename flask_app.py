#!/usr/bin/env python


import app
# from config import production_config as config
from config import developer_config as config
from flask_sslify import SSLify

app = app.init_app(config)
sslify = SSLify(app)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
