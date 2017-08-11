from . import geolocation_blueprint
from app.user_model.user_model import User
from .model import Geolocation

from flask import g, request, jsonify, session
import requests


@geolocation_blueprint.before_request
def before_request():
    g.permission = User.auth()


@geolocation_blueprint.route('/geolocation', methods=['POST'])
def save_geolocation():
    if g.permission < 1:
        return jsonify({'response': 'you have no permissions!!'})
    if request.method == 'POST':
        location_dict = request.get_json()
        lat = None
        lon = None
        if location_dict['method'] == 'coordinates':
            lat = location_dict['latitude']
            lon = location_dict['longitude']
        elif location_dict['method'] == 'ip':
            r = requests.get("http://freegeoip.net/json/178.214.196.34")
            lat = r.json()['latitude']
            lon = r.json()['longitude']
        if lat is not None and lon is not None:
            Geolocation.update_geolocation(session['id'], lat, lon)
        return jsonify({'response': 'OK'})
