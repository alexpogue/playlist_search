import json

from flask import Blueprint, request, abort, jsonify, render_template
from ..models.goal import Goal
from ..models.base import db

from ..models.goal import goal_schema, goals_schema

from flask_marshmallow import pprint

root_api_blueprint = Blueprint('root_api', __name__)

@root_api_blueprint.route('/')
def get_goals():
    return render_template('index.html')
