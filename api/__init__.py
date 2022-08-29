"""Welcome to the documentation for the Doctorly API Project!

This project is written in Python, with the
[Flask](https://flask.palletsprojects.com/) web framework. This documentation
is generated automatically from the
[project's source code](https://github.com/zain232/docterlyapi) using
the [APIFairy](https://github.com/miguelgrinberg/apifairy) Flask extension.

## Project Overview

Obtaining an appointment with a doctor for a checkup is commonly observed to
be time consuming and demanding. Usually, there are already boo
ked slots and long waiting lists, so going to the hospital or clinic goes in vain. 
A patient may be late for a new appointment for any reason, and the 
slot may be filled by someone else.
We devised a solution to these issues. By utilizing this API, a user can check
the available slots for a doctor he wishes to see, from home. The patient
does not have to stand in long lines to learn about the doctor's expenses or
know the free slots or to get an appointment. All of this can be done from 
any client application

## Features
- User registration, login and logout
- Search functionality to search for doctors by different attributes
- Separate endpoints for Doctor like registration and creation of profile.
- Complete appointment history

## Limitations
- No endpoints for rating a doctor
- Ideally, /doctors/popular/doctors endpoint should return the doctors based on their rating and some other attributes but as of current implementation returns the random doctors.

## Future Expansions
- Email recovery and password reset support
- Real time Notifications
- More advanced search functionality
- A client application that consumes this API
- Inclusion of rating endpoints
- Patient's prescription, recommended diet plan, next appointment date
- A robust algorithm that filters the top doctors
- Unit testing
"""

from flask import Flask, url_for, redirect, request
from apifairy import APIFairy
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from flask_migrate import Migrate
from flask_admin import Admin
from flask_login import LoginManager
from api.config import ProductionConfig as Config
from flask_admin.base import AdminIndexView
from flask_caching import Cache
from api.search.redis_search import RedisSearchApi
import redis

api_fairy = APIFairy()
db = SQLAlchemy()
ma = Marshmallow()
basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth()
migrate = Migrate()
admin_manager = Admin()
login_manager = LoginManager()
login_manager.login_view = "admin.sign_in"
login_manager.login_message_category = "info"
cache = Cache()
client =  redis.Redis(host='redisdb', port=6379)
search_api = RedisSearchApi(client)

def create_app(config=Config):
    app = Flask(__name__)
    app.config.from_object(Config)
    initialize_extensions(app)
    register_blueprints(app)
    return app

def initialize_extensions(app):
    api_fairy.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    cache.init_app(app)
    search_api.init_app(app)

    # Restricting the admin panel index route
    from flask_login import current_user
    class RestrictIndexView(AdminIndexView):
        def is_accessible(self):
            return current_user.is_authenticated and current_user.role.role_name == 'admin'
        
        def inaccessible_callback(self, name, **kwargs):
            # redirect to login page if user doesn't have access
            return redirect(url_for('web_admin.sign_in'))
    
    admin_manager.init_app(app, index_view=RestrictIndexView())

def register_blueprints(app):
    from api.webadmin import web_admin
    from api.auth import auth 
    from api.doctor import doctor
    from api.patient import patient 
    from api.user import users
    from api.misc import misc
    from api.commands import commands
    from api.errors import errors

    app.register_blueprint(web_admin, url_prefix="/adminpanel")
    app.register_blueprint(users, url_prefix="/users")
    app.register_blueprint(auth, url_prefix="/auth")
    app.register_blueprint(doctor, url_prefix="/doctors", name="doctors")
    app.register_blueprint(patient, url_prefix="/patient", name="patients")
    app.register_blueprint(misc, url_prefix="/misc")
    app.register_blueprint(commands)
    app.register_blueprint(errors)