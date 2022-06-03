from api.auth import auth_bp
from api import basic_auth, token_auth, db
from apifairy  import authenticate, body, other_responses, response
from api.models import User



@auth_bp.route("/tokens", methods=["POST"])
@authenticate(basic_auth)
@response()
@other_responses({401: "Invalid username or password"})
def get_token():
    token = basic_auth.current_user().get_token()
    db.session.commit()

    
