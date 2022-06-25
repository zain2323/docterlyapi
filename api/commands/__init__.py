from flask import Blueprint

commands = Blueprint("commands", __name__)

from api.commands import jobs