from urllib.parse import quote
import json

# class ProductionConfig:
#     with open("/etc/secrets.json", "r") as secrets_file:
#         config = json.load(secrets_file)
#     SECRET_KEY = config.get("SECRET_KEY")
#     UPLOAD_FOLDER = './api/static/results'
#     MAIL_SERVER = "smtp.googlemail.com"
#     MAIL_PORT = "587"
#     MAIL_USE_TLS = "1"  
#     MAIL_USERNAME = config.get("MAIL_USERNAME")
#     MAIL_PASSWORD = config.get("MAIL_PASSWORD")
#     ADMINS = [config.get("EMAIL")]
#     SUBSCRIPTION_KEY = config.get("SUBSCRIPTION_KEY")
#     ENDPOINT = config.get("ENDPOINT")
#     REDIS_URL = 'redis://'
#     FLASK_ENV = "production"
#     TESTING = False
#     SQLALCHEMY_DATABASE_URI = f'postgresql://{config.get("DB_ROLE")}:%s@{config.get("HOST")}/{config.get("DB_NAME")}' % quote(config.get("DB_PASSWORD"))
#     SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig:
    FLASK_ENV = "development"
    SECRET_KEY = "'0035ce4c6d1f0d6f327d97051b9bcfafc7d922b2ce06c4f7dbff5ee4d159b50f'"
    APIFAIRY_TITLE = 'Doctorly API'
    APIFAIRY_VERSION = '0.1'
    APIFAIRY_UI = 'elements'
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
