from flask import Blueprint

geolocation_blueprint = Blueprint('geolocation', __name__)

from . import controller
