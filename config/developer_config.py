import os

# required for forms
ADMINS = ['ladonya.s@gmail.com']
DEBUG = False
TESTING = False
WTF_CSRF_ENABLED = True
SECRET_KEY = 'very the last secret'

# Database configuration
SQL_HOST = 'localhost'
SQL_USER ='root'
SQL_PASSWORD = '3121712'
SQL_DB = 'matcha'
LOGFILE = 'log.txt'

ROOT_DIRECTORY = os.getcwd()
# GEO_API_KEY = 'AIzaSyDTjHE4Vvo4tF82ecnk_X1-wdX4jZK1M78'
