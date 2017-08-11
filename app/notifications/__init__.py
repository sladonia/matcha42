from flask import Blueprint

notifications_blueprint = Blueprint('controller', __name__)

from . import controller

