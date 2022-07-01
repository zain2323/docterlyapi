from api.patient.schema import (PatientSchema, patients_schema, AppointmentSchema,
         ReturnAppointmentSchema, AppointmentHistorySchema)
from api.models import Patient, User, BookedSlots, Event, Slot, Appointment
from api import token_auth, db 
from apifairy import response, body, authenticate, other_responses
from api.patient import patient
from api.doctor.schema import TimingsSchema
from datetime import datetime, date , timedelta
from api.doctor.utils import get_experience

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
    """Returns all the registered patients for the currently authenticated user"""
    current_user = token_auth.current_user()
    patients = current_user.patient
    return patients
    
@patient.route("/get/<int:id>", methods=["GET"])
@authenticate(token_auth)
@response(PatientSchema)
@other_responses({404: "Patient not found"})
def get_patient(id):
    """Get patient by the id"""
    return Patient.query.get_or_404(id)

@patient.route("/new_appointment", methods=["POST"])
@authenticate(token_auth)
@body(AppointmentSchema)
@response(ReturnAppointmentSchema)
def create_appointment(kwargs):
    """Create a new appointment for the given patient id"""
    user = token_auth.current_user()
    # Getting all the ids from the request body
    patient_id = kwargs["patient_id"]
    slot_id = kwargs["slot_id"]
    # Getting all the database entries from the given ids
    patient = Patient.query.get(patient_id)
    slot = Slot.query.get(slot_id)
    event = slot.get_latest_event()
    # Creating appointment entry
    appointment = Appointment(slot=slot, patient=patient, event=event)
    db.session.add(appointment)
    # Incrementing the booked slots by 1
    booked_slot = event.get_latest_event_info()
    # Calculating the expected time of the patient's appointment
    diff = booked_slot.slots_booked * slot.appointment_duration
    expected_time = get_patient_appointment_time(slot.start, diff)
    booked_slot.increment_slot()
   
    # Creating the response object
    occurring_date = event.occurring_date
    timings = {"slot": slot, "occurring_date": occurring_date, "slots_booked": booked_slot.slots_booked}
    response = {"timings": timings, "patient": patient, "expected_time": expected_time}
    
    db.session.commit() 
    return response

def get_patient_appointment_time(start, diff):
    end = datetime.combine(date.today(), start) + timedelta(minutes=diff)
    return end.time()

@patient.route("/appointment/history", methods=["GET"])
@authenticate(token_auth)
@response(AppointmentHistorySchema(many=True))
def appointment_history():
    """Returns the appointment history for the currently authenticated user"""
    current_user = token_auth.current_user()
    # Getting all the patients registered under the authenticated user
    patients = current_user.patient
    response = []
    for patient in patients:
        # Getting all the appointments
        appointments = patient.appointment
        for appointment in appointments:
            slot = appointment.slot
            doctor = slot.doctor
            doctor = prepare_doctor_info(doctor)
            event = slot.get_latest_event()
            occurring_date = event.occurring_date
            booked_slot = event.get_latest_event_info().slots_booked
            # Timings dict
            timings = {"slot": slot, "occurring_date": occurring_date, "slots_booked": booked_slot}
            # COnstructing the final response object
            response.append({"patient": patient, "doctor": doctor, "timings": timings})
    return response

def prepare_doctor_info(doctor):
    user = doctor.user
    id = doctor.id
    description = doctor.description
    qualifications = doctor.get_doctor_qualifications_and_info()
    experience = get_experience(qualifications)    
    specializations = doctor.specializations[0]
    return {"id": id, "description": description, "experience":experience, "specializations": specializations, 'qualifications': qualifications,  "user": user}

