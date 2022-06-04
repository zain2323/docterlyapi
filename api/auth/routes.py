from api.auth import auth
from api import basic_auth, token_auth, db
from apifairy  import authenticate, body, other_responses, response
from api.auth.schema import TokenSchema
from api.models import User
from api.auth import auth


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
    
