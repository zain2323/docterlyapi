from flask import Blueprint

auth_bp = Blueprint("auth_bp", __name__)

from api.auth import routes, schema, authentication
