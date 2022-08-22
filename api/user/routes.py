from api.user import users
from apifairy import authenticate, body, response, other_responses
from api.user.schema import UserSchema
from api.models import User
from api import db, basic_auth, token_auth

@users.route("/register", methods=["POST"])
@body(UserSchema(only=["name","email", "password", "role"]))
@response(UserSchema, 201)
def register(kwargs):
    """Registers a new user"""
    print(kwargs)
    new_user = User(**kwargs)
    print(new_user)
    password = kwargs["password"]
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    return new_user

@users.route("/info", methods=["GET"])
@authenticate(token_auth)
@response(UserSchema, 200)
def get_account_info():
    """Get the currently authenticated user's info"""
    return token_auth.current_user()
