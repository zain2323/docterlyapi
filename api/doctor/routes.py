from api.models import Doctor, User, Specialization, Qualification, doctor_qualifications
from api import db, basic_auth, token_auth
from apifairy import response, other_responses, body, authenticate
from api.doctor import doctor
from api.doctor.schema import (CreateNewDoctorSchema, DoctorSchema, doctors_schema, 
    DoctorQualifications, DoctorSpecializations, DoctorInfoSchema)

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
@response(DoctorInfoSchema)
def get_current_doctor_info():
    """Get the currently authenticated doctor's info"""
    current_user = token_auth.current_user()
    doctor = Doctor.query.filter_by(user=current_user).first()
    qualifications_info = doctor.get_doctor_qualifications_and_info()
    doctor_info = prepare_doctor_info(doctor, qualifications_info)
    print(doctor_info)
    return doctor_info

def prepare_doctor_info(doctor, qualifications_info):
    doctor_schema = DoctorSchema()
    qualifications_info_schema = DoctorQualifications()
    doctor_dict = doctor_schema.dump(doctor)
    qualifications_info_dict = qualifications_info_schema.dump(qualifications_info)
    doctor_dict["qualifications"] = qualifications_info_dict
    return doctor_dict

@doctor.route("/all", methods=["GET"])
@authenticate(token_auth)
@response(doctors_schema)
def get_all():
    """Returns all the registered doctors"""
    return Doctor.query.all()
    
@doctor.route("/get/<int:id>", methods=["GET"])
@authenticate(token_auth)
@response(DoctorSchema)
@other_responses({404: "Doctor not found"})
def get_doctor(id):
    """Get doctor by the id"""
    return Doctor.query.get_or_404(id)

@doctor.route("/add_specializations", methods=["POST"])
@authenticate(token_auth)
@body(DoctorSpecializations)
@response(DoctorSpecializations, 200)
def add_specializations(specializations):
    """Add specializations"""
    current_user = token_auth.current_user()
    doctor = current_user.doctor[0]
    if doctor is None:
        abort(401)
    for specialization in specializations.values():
        specialization = specialization[0]
        specialization_db = Specialization.query.filter_by(name=specialization).first()
        doctor.add_specialization(specialization_db)
    db.session.commit()
    return specializations

@doctor.route("/add_qualifications", methods=["POST"])
@authenticate(token_auth)
@body(DoctorQualifications)
@response(DoctorQualifications, 200)
def add_qualfications(qualifications):
    """Add qualifications"""
    current_user = token_auth.current_user()
    doctor = current_user.doctor[0]
    if doctor is None:
        abort(401)
    qualification_name, procurement_year, institute_name = parse_qualification_body(qualifications)
    for i in range(len(qualification_name)):
        name = qualification_name[i]
        year = procurement_year[i]
        ins_name = institute_name[i]
        qualification_db = Qualification.query.filter_by(name=name).first()
        doctor.add_qualification(qualification_db, year, ins_name)
    db.session.commit()
    return qualifications

def parse_qualification_body(qualification_body):
    qualifications = qualification_body["qualification_name"]
    procurement_year = qualification_body["procurement_year"]
    institute_name = qualification_body["institute_name"]
    return qualifications, procurement_year, institute_name

def create_slot():
    """Create your available slots"""

def get_all_patients():
    """Returns all of your patients"""

def get_appointment_patients(appointment_id):
    """Returns all the patients of the particular appointment id"""




    
