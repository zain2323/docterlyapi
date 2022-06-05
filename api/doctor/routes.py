from api.models import Doctor, User
from api import db, basic_auth, token_auth
from apifairy import response, other_responses, body, authenticate
from api.doctor import doctor
from api.doctor.schema import CreateNewDoctorSchema, DoctorSchema

@doctor.route("/new", methods=["POST"])
@body(CreateNewDoctorSchema)
@response(DoctorSchema)
def new(kwargs):
    """Registers a new doctor"""
    description = kwargs.pop("description")
    new_user = User(**kwargs)
    password = kwargs["password"]
    new_user.set_password(password)
    new_doctor = Doctor(user=new_user, description=description)
    db.session.add(new_doctor)
    db.session.add(new_user)
    db.session.commit()
    return new_doctor

@doctor.route("/info", methods=["GET"])
@authenticate(token_auth)
@response(DoctorSchema)
def get_current_doctor_info():
    """Get the currently authenticated doctor's info"""
    current_user = token_auth.current_user()
    return Doctor.query.filter_by(user=current_user).first()
    
    
    
