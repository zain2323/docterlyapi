from apifairy import authenticate, response, body
from api.models import Specialization, Doctor, Qualification
from api.misc import misc
from api import token_auth, db
from api.webadmin.schema import SpecializationSchema, QualificationSchema
from api.doctor.schema import DoctorSchema, DoctorInfoSchema
from api.doctor.utils import get_experience, generate_hex_name, save_picture, delete_picture
from werkzeug.utils import secure_filename
from flask import abort, request, jsonify, url_for

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_url(filename="default_doctor_img.jpg"):
    return url_for("static", filename="doctor_profile_pics/"+filename, _external=True)

def prepare_doctor_info(doctor, qualifications_info):
    user = doctor.user
    id = doctor.id
    description = doctor.description
    qualifications = qualifications_info
    try:
        specializations = doctor.specializations[0]
    except:
        specializations = {}
    experience = get_experience(qualifications)
    url = generate_url(filename=doctor.image)
    slot = doctor.slots
    return {"id": id, "user": user, "description": description, "experience": experience, "image": url, "specializations": specializations, 'qualifications': qualifications, "slot": slot}


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
@response(DoctorInfoSchema(many=True))
def get_doctors_by_specialization(specialization_id):
    """Returns all the doctors with the given specialization id"""
    specialization = Specialization.query.get_or_404(specialization_id)
    doctors = []
    doctors_db = Doctor.query.filter(Doctor.specializations.contains(specialization)).all()
    for doctor in doctors_db:
        qualifications = doctor.get_doctor_qualifications_and_info()
        doctor = prepare_doctor_info(doctor, qualifications)
        doctors.append(doctor)
    return doctors

@misc.route("/doctors/qualification/<int:qualification_id>")
@authenticate(token_auth)
@response(DoctorInfoSchema(many=True))
def get_doctors_by_qualification(qualification_id):
    """Returns all the doctors with the given qualification id"""
    qualification = Qualification.query.get_or_404(qualification_id)
    doctors_db = Doctor.query.filter(Doctor.qualifications.contains(qualification)).all()
    doctors = []
    for doctor in doctors_db:
        qualifications = doctor.get_doctor_qualifications_and_info()
        doctor = prepare_doctor_info(doctor, qualifications)
        doctors.append(doctor)
    return doctors


@misc.route("/image/<int:specialization_id>", methods=["POST"])
@authenticate(token_auth)
def upload_image(specialization_id):
    """Uploads the specialization picture with the given id"""
    specialization = Specialization.query.get(specialization_id)
    if specialization is None:
        abort(404)
    if "file" not in request.files or request.files["image"].filename == "":
       image = "allergist.jpg"
    image = request.files["image"]
    if image and allowed_file(image.filename):
        filename = secure_filename(image.filename)
        filename = generate_hex_name()
        filename = save_picture(image, filename, loc='./api/static/specialization_images')
    else:
        resp = jsonify({"message": "Invalid file"})
        return resp
    # Fetching the old image
    old_image = specialization.image
    if old_image != "allergist.jpg":
        delete_picture(old_image, loc="./api/static/specialization_images/")
    specialization.image = filename
    db.session.commit()
    return jsonify({"message": "specialization picture changed"})

@misc.route("/search/<int:specialization_id>", methods=["GET"])
@authenticate(token_auth)
@response(DoctorInfoSchema(many=True))
def search(specialization_id):
    """Search any doctor with the name of the given specialization id"""
    specialization = Specialization.query.get(specialization_id)
    if specialization is None:
        return abort(404)
    name = request.args.get("name", default=" ")
    query = f"""SELECT doctor.id FROM doctor JOIN "user" ON "user"."id" = doctor.id WHERE "user".name LIKE'%{name}%';"""
    result = db.session.execute(query).filter(Doctor.specializations.contains(specialization)).all()
    doctors = []
    for doc_id in result:
        doctor = Doctor.query.get(doc_id[0])
        doctors.append(doctor)
    sp_doctors = Doctor.query.filter(Doctor.specializations.contains(specialization)).all()
    result = []
    
    return doctors

    