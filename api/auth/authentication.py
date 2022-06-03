from api.models import User
from api import basic_auth, token_auth
from werkzeug.exceptions import Forbidden, Unauthorized

@basic_auth.verify_password
def verify_password(email , password):
    user = User.query.filter_by(email=email).first()
    print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
    print(email, password)
    if user is None:
        return None
    print(user)
    if user.verify_password(password):
        return user

@basic_auth.error_handler
def basic_auth_error(status=401):
    error = (Forbidden if status == 401 else Unauthorized)()
    return {
        "code": error.code,
        "message": error.name,
        "description": error.description
    }, error.code, {'WWW-Authenticate': 'Form'}

@token_auth.verify_token
def verify_token(auth_token):
    return User.verify_token(auth_token)

@token_auth.error_handler
def token_auth_error(status=401):
    error = (Forbidden if status == 403 else Unauthorized)()
    return {
        'code': error.code,
        'message': error.name,
        'description': error.description,
    }, error.code
