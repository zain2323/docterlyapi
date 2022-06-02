from flask import Flask
from apifairy import APIFairy
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from flask_migrate import Migrate
from api.config import DevelopmentConfig as Config

api_fairy = APIFairy()
ma = Marshmallow()
db = SQLAlchemy()
basic_auth = HTTPBasicAuth()
token = HTTPTokenAuth()
migrate = Migrate()

def create_app(config=Config):
    app = Flask(__name__)
    app.config.from_object(Config)
    initialize_extensions(app)
    register_blueprints(app)

    from api import models
    return app

def initialize_extensions(app):
    api_fairy.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)

def register_blueprints(app):
    pass