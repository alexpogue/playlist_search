import json

from flask import Blueprint, request, abort, jsonify, render_template
from flask_httpauth import HTTPBasicAuth
from ..models.base import db

from werkzeug.security import generate_password_hash, check_password_hash

from flask_marshmallow import pprint

root_api_blueprint = Blueprint('root_api', __name__)

auth = HTTPBasicAuth()

users = {
    'student': generate_password_hash('buildaband')
}

@auth.verify_password
def verify_password(username, password):
    if username in users:
        return check_password_hash(users.get(username), password)
    return False

@root_api_blueprint.route('/')
@auth.login_required
def get_goals():
    return render_template('index.html')
