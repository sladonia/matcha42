from flask import Blueprint

main_blueprint = Blueprint('routes', __name__)

from . import routes
