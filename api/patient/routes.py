from api.patient.schema import PatientSchema, patients_schema
from api.models import Patient, User
from api import token_auth, db 
from apifairy import response, body, authenticate, other_responses
from api.patient import patient

@patient.route("/new", methods=["POST"])
@authenticate(token_auth)
@body(PatientSchema)
@response(PatientSchema)
def new(kwargs):
    """Registers a new patient"""
    current_user = token_auth.current_user()
    new_patient = Patient(**kwargs)
    new_patient.user_id = current_user.id
    db.session.add(new_patient)
    db.session.commit()
    return new_patient

@patient.route("/info", methods=["GET"])
@authenticate(token_auth)
@response(patients_schema, 200)
def get_all_patients():
    """Get all patients of the authenticated user"""
    current_user = token_auth.current_user()
    patients = Patient.query.filter_by(user=current_user).all()
    return patients


@patient.route("/all", methods=["GET"])
@authenticate(token_auth)
@response(patients_schema)
def get_all():
    """Returns all the registered patients"""
    return Patient.query.all()
    
@patient.route("/get/<int:id>", methods=["GET"])
@authenticate(token_auth)
@response(PatientSchema)
@other_responses({404: "Patient not found"})
def get_patient(id):
    """Get patient by the id"""
    return Patient.query.get_or_404(id)