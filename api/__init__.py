from flask import Flask
from apifairy import APIFairy
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from flask_migrate import Migrate
from api.config import DevelopmentConfig as Config

api_fairy = APIFairy()
db = SQLAlchemy()
ma = Marshmallow()
basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth()
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
    from api.user import users
    from api.auth import auth
    from api.doctor import doctor
    from api.patient import patient

    app.register_blueprint(users, url_prefix="/users")
    app.register_blueprint(auth, url_prefix="/auth")
    app.register_blueprint(doctor, url_prefix="/doctor")
    app.register_blueprint(patient, url_prefix="/patient")