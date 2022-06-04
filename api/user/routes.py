from api.user import users
from apifairy import authenticate, body, response, other_responses
from api.user.schema import UserSchema
from api.models import User
from api import db, basic_auth, token_auth

@users.route("/register", methods=["POST"])
@body(UserSchema)
@response(UserSchema, 201)
def register(kwargs):
    """Registers a new user"""
    new_user = User(**kwargs)
    password = kwargs["password"]
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    return new_user

@users.route("/info", methods=["GET"])
@authenticate(token_auth)
@response(UserSchema, 200)
def get_account_info():
    """Displays the account info of the currently logged in user"""
    return token_auth.current_user()



