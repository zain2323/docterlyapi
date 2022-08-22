import json

class ProductionConfig:
    with open("/etc/secrets.json", "r") as secrets_file:
        config = json.load(secrets_file)
    APIFAIRY_TITLE = 'Doctorly API'
    APIFAIRY_VERSION = '0.1'
    APIFAIRY_UI = 'elements'
    FLASK_ADMIN_SWATCH = 'cyborg'
    JSON_SORT_KEYS = False
    SECRET_KEY = config.get("SECRET_KEY")
    UPLOAD_FOLDER = './api/static/doctor_profile_pics'
    MAIL_SERVER = "smtp.googlemail.com"
    MAIL_PORT = "587"
    MAIL_USE_TLS = "1"  
    MAIL_USERNAME = config.get("MAIL_USERNAME")
    MAIL_PASSWORD = config.get("MAIL_PASSWORD")
    ADMINS = [config.get("EMAIL")]
    FLASK_ENV = "production"
    TESTING = False
    PGPASSWORD = config.get("PGPASSWORD")
    SQLALCHEMY_DATABASE_URI = f'postgresql://{config.get("DB_ROLE")}:{config.get("DB_PASSWORD")}@{config.get("HOST")}/{config.get("DB_NAME")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Redis config
    CACHE_TYPE = "redis"
    CACHE_REDIS_HOST = "redis"
    CACHE_REDIS_PORT = "6379"
    CACHE_REDIS_DB = "0"
    CACHE_REDIS_URL = "redis://localhost:6379/0"
    CACHE_DEFAULT_TIMEOUT = "500"

class DevelopmentConfig:
    FLASK_ENV = "development"
    SECRET_KEY = "'0035ce4c6d1f0d6f327d97051b9bcfafc7d922b2ce06c4f7dbff5ee4d159b50f'"
    APIFAIRY_TITLE = 'Doctorly API'
    APIFAIRY_VERSION = '0.1'
    APIFAIRY_UI = 'elements'
    FLASK_ADMIN_SWATCH = 'cyborg'
    FLASK_DEBUG = True
    TESTING = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///data.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_SORT_KEYS = False

class PostgresqlTestingConfig:
    FLASK_ENV = "development"
    SECRET_KEY = "'0035ce4c6d1f0d6f327d97051b9bcfafc7d922b2ce06c4f7dbff5ee4d159b50f'"
    APIFAIRY_TITLE = 'Doctorly API'
    APIFAIRY_VERSION = '0.1'
    APIFAIRY_UI = 'elements'
    FLASK_DEBUG = True
    TESTING = False
    SQLALCHEMY_DATABASE_URI = 'postgresql://doctorly_user:doctorly@localhost/doctorly_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
