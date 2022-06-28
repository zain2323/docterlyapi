from api.auth import auth
from api import basic_auth, token_auth, db
from apifairy  import authenticate, body, other_responses, response
from api.auth.schema import TokenSchema
from api.models import User
from api.auth import auth
from flask import jsonify


@auth.route("/get_token", methods=["POST"])
@authenticate(basic_auth)
@response(TokenSchema)
@other_responses({401: "Invalid username or password"})
def get_auth_token():
    """Get the authentication token"""
    user = basic_auth.current_user()
    token = user.get_token()
    db.session.commit()
    return dict(token=token)

@auth.route("/logout", methods=["PUT"])
@authenticate(token_auth)
def logout():
    """Logout the currently authenticated user"""
    user = token_auth.current_user()
    user.token = None
    user.token_expiration = None
    db.session.commit()
    return jsonify({"message": "Token Revoked"})
