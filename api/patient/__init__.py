from flask import Blueprint

patient = Blueprint("patient", __name__)

from api.patient import routes, schema