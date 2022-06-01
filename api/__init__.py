from flask import Flask
from apifairy import APIFairy
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from flask_migrate import Migrate

api_fairy = APIFairy()
ma = Marshmallow()
db = SQLAlchemy()
basic_auth = HTTPBasicAuth()
token = HTTPTokenAuth()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    initialize_extensions(app)
    initialize_extensions(app)
    return app

def initialize_extensions(app):
    api_fairy.init_app(app)
    db.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)

def register_blueprints(app):
    pass