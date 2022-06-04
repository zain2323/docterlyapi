from flask import Blueprint

doctor = Blueprint("doctor", __name__)

from api.doctor import routes, schema