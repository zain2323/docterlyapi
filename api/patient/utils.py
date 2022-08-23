from datetime import datetime, date , timedelta
from flask import url_for

def prepare_doctor_info(doctor):
    user = doctor.user
    id = doctor.id
    description = doctor.description
    qualifications = doctor.get_doctor_qualifications_and_info()
    experience = get_experience(qualifications)    
    specializations = doctor.specializations[0]
    url = generate_url(filename=doctor.image)
    rating = "4.7"
    no_of_patients = get_patient_count(doctor)
    return {"id": id, "description": description, "no_of_patients": no_of_patients, "rating": rating, "experience":experience, "image": url, "specializations": specializations, 'qualifications': qualifications,  "user": user}

def generate_url(filename="default_doctor_img.jpg"):
    return url_for("static", filename="doctor_profile_pics/"+filename, _external=True)

def get_patient_appointment_time(start, diff):
    end = datetime.combine(date.today(), start) + timedelta(minutes=diff)
    return end.time()