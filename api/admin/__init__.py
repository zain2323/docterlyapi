from flask import Blueprint

admin = Blueprint("admin", __name__)

from api.admin import routes, schema