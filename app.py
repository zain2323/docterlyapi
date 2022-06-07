from api import create_app
from api.models import *
from api.doctor.schema import *
from api.user.schema import *
from api.auth.schema import *
from flask import redirect, url_for

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
            "db": db, "User": User, "Doctor": Doctor, "Patient": Patient, "Specialization": Specialization,
            "Qualification": Qualification, "Day": Day, "Appointment": Appointment, "Slot": Slot,
            "Rating": Rating, "Prescription": Prescription, "Role": Role, "PrescribedMedicines": PrescribedMedicines,
            "doctor_specializations": doctor_specializations, "doctor_qualifcations": doctor_qualifications,
            "UserSchema": UserSchema, "DoctorSchema": DoctorSchema, "CreateNewDoctorSchema": CreateNewDoctorSchema,
            "RoleSchema": RoleSchema, "TokenSchema": TokenSchema, "QualificationSchema": QualificationSchema,
            "SpecializationSchema": SpecializationSchema
           }

@app.route('/')
def index(): 
    return redirect(url_for('apifairy.docs'))

if __name__ == 'main':
    app.run(debug=True)