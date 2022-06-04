from api.models import Doctor
from api import db, basic_auth, token_auth
from apifairy import response, other_responses, body, authenticate
from api.doctor import doctor

@doctor.route("/new_doctor", methods=["POST"])
def new(kwargs):
    """Registers a new doctor"""
    
