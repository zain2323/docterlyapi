from apifairy import authenticate, response, body
from api.models import Specialization, Doctor, Qualification
from api.misc import misc
from api import token_auth
from api.webadmin.schema import SpecializationSchema, QualificationSchema
from api.doctor.schema import DoctorSchema

@misc.route("/specializations", methods=["GET"])
@authenticate(token_auth)
@response(SpecializationSchema(many=True))
def get_specializations():
    """Returns all the specializations"""
    return Specialization.query.all()

@misc.route("/qualifications", methods=["GET"])
@authenticate(token_auth)
@response(QualificationSchema(many=True))
def get_qualifications():
    """Returns all the qualifications"""
    return Qualification.query.all()

@misc.route("/doctors/specialization/<int:specialization_id>")
@authenticate(token_auth)
@response(DoctorSchema(many=True))
def get_doctors_by_specialization(specialization_id):
    """Returns all the doctors with the given specialization id"""
    specialization = Specialization.query.get_or_404(specialization_id)
    return Doctor.query.filter(Doctor.specializations.contains(specialization)).all()

@misc.route("/doctors/qualification/<int:qualification_id>")
@authenticate(token_auth)
@response(DoctorSchema(many=True))
def get_doctors_by_qualification(qualification_id):
    """Returns all the doctors with the given qualification id"""
    qualification = Qualification.query.get_or_404(qualification_id)
    return Doctor.query.filter(Doctor.qualifications.contains(qualification)).all()
