from flask import url_for
from api.doctor.utils import get_experience, get_patient_count
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
    rating = "4.7"
    no_of_patients = get_patient_count(doctor)
    slot = doctor.slots
    return {"id": id, "user": user, "description": description, "no_of_patients": no_of_patients, "rating": rating, "experience": experience, "image": url, "specializations": specializations, 'qualifications': qualifications, "slot": slot}

def parse_names(names_list):
    parsed = ""
    for name in names_list:
        parsed += name +  ":* | "
    return parsed[:len(parsed)-2]