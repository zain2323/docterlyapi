from flask import Blueprint

misc = Blueprint("misc", __name__)

from api.misc import routes, schema