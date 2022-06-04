from flask import Blueprint

users = Blueprint("users", __name__)

from api.user import routes, schema