from flask import Blueprint

doctor = Blueprint("patient", __name__)

from api.patient import routes, schema