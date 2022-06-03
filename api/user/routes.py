from api.user import user_bp
from apifairy import authenticate, body, response, other_responses
from api.user.schema import UserSchema
from api.models import User
from api import db, basic_auth

@user_bp.route("/register", methods=["POST"])
@body(UserSchema)
@response(UserSchema, 201)
def register(kwargs):
    """Registers a new user"""
    print(kwargs)
    new_user = User(**kwargs)
    password = kwargs["password"]
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    return new_user

