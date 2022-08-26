from api import create_app, api_fairy, search_api
from api.models import *
from api.doctor.schema import *
from api.user.schema import *
from api.auth.schema import *
from flask import redirect, url_for

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
            "search_api": search_api, "db": db, "User": User, "Doctor": Doctor, "Patient": Patient, "Specialization": Specialization,
            "Qualification": Qualification, "Day": Day, "Appointment": Appointment, "Slot": Slot,
            "Rating": Rating, "Role": Role,
            "doctor_specializations": doctor_specializations, "doctor_qualifications": doctor_qualifications,
            "BookedSlots": BookedSlots, "Event": Event, "EventMeta": EventMeta,
            "UserSchema": UserSchema, "DoctorSchema": DoctorSchema, "CreateNewDoctorSchema": CreateNewDoctorSchema,
            "RoleSchema": RoleSchema, "TokenSchema": TokenSchema, "QualificationSchema": QualificationSchema,
            "SpecializationSchema": SpecializationSchema
           }

@app.before_first_request
def sync_db():
    doctors = Doctor.query.all()
    from api.search.syncronizer import Syncronizer    
    sync = Syncronizer(doctors)
    sync.sync()

@app.route('/')
def index():
    return redirect(url_for('apifairy.docs'))

if __name__ == 'main':
    app.run(debug=True)