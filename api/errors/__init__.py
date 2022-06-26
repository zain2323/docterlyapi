from flask import Blueprint

errors = Blueprint("errors", __name__)

from api.errors import error_handling