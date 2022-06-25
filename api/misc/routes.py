from apifairy import authenticate, response, body
from api.models import Specialization, Doctor
from api.misc import misc
from api import token_auth
from api.webadmin.schema import SpecializationSchema
from api.doctor.schema import DoctorSchema

@misc.route("/specializations", methods=["GET"])
@authenticate(token_auth)
@response(SpecializationSchema(many=True))
def get_specializations():
    """Returns all the specializations"""
    return Specialization.query.all()

@misc.route("/docotors/<int:specialization_id>")
@authenticate(token_auth)
@response(DoctorSchema(many=True))
def get_doctors_by_specialization(specialization_id):
    """Returns all the doctors with the given specialization id"""
    specialization = Specialization.query.get_or_404(specialization_id)
    return Doctor.query.filter_by(specializations=specialization).all()
