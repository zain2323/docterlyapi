from flask import Blueprint

search = Blueprint("search", __name__)

from api.search import doctor, routes