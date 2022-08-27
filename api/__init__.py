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
# from redis_om import get_redis_connection
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