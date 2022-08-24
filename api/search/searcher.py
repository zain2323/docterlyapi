from api.models import Doctor, User, Slot, Specialization, Qualification

def add_doctor(doctor):
    payload = {}

    payload["id"] = doctor.id
    payload["description"] = doctor.description
    payload["image"] = doctor.image
    payload["rating"] = doctor.rating
    payload["user"] = doctor.user
    print(payload)

def add_qualifications(qualifications):
    pass

def add_specializations(specializations):
    pass

def update():
    pass

def remove():
    pass