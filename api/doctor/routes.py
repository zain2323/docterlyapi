from api.models import (Doctor, User, Specialization, Qualification, doctor_qualifications, Slot, Day,
                        Event, EventMeta, BookedSlots, Appointment, Patient)    
from api import db, basic_auth, token_auth, cache
from apifairy import response, other_responses, body, authenticate
from api.doctor import doctor
from api.doctor.schema import (CreateNewDoctorSchema, DoctorSchema, doctors_schema, 
    DoctorQualifications, DoctorSpecializations, DoctorInfoSchema, CreateNewSlot, ReturnSlot, TimingsSchema)
from datetime import timedelta, date, datetime, time
from api.patient.schema import PatientSchema
from flask import abort, request, jsonify, url_for
from api.doctor.utils import (parse_qualification_body, prepare_doctor_info, get_experience, generate_hex_name,
                             save_picture, delete_picture, get_patient_count, update_doctor_cache, 
                             does_doctor_cache_needs_update, calculate_end_time, create_event, create_event_meta)
from werkzeug.utils import secure_filename
from math import ceil
from api.doctor.decorators import cache_response_with_id, cache_response_with_token

@doctor.route("/new", methods=["POST"])
@body(CreateNewDoctorSchema)
@response(DoctorSchema)
def new(kwargs):
    """Registers a new doctor"""
    description = kwargs.pop("description")
    new_user = User(**kwargs)
    password = kwargs["password"]
    new_user.set_password(password)
    new_doctor = Doctor(user=new_user, description=description, image="default_doctor_image.jpg")
    db.session.add(new_doctor)
    db.session.add(new_user)
    db.session.commit()
    update_doctor_cache(update=True)
    return new_doctor

@doctor.route("/image/", methods=["POST"])
@authenticate(token_auth)
def upload_image():
    """Uploads the profile picture of the currently authenticated doctor"""
    current_user = token_auth.current_user()
    doctor = current_user.doctor
    if doctor == []:
        abort(401)
    doctor = doctor[0] 
    if "file" not in request.files or request.files["image"].filename == "":
       image = "default_doctor_img.jpg"
    image = request.files["image"]
    if image and allowed_file(image.filename):
        filename = secure_filename(image.filename)
        filename = generate_hex_name()
        filename = save_picture(image, filename)
    else:
        resp = jsonify({"message": "Invalid file"})
        return resp
    # Fetching the old image
    old_image = doctor.image
    if old_image != "default_doctor_image.jpg":
        delete_picture(old_image)
    doctor.image = filename
    db.session.commit()
    return jsonify({"message": "profile picture changed"})
        
@doctor.route("/info", methods=["GET"])
@authenticate(token_auth)
@cache_response_with_token(prefix="current_user", token=token_auth)
@response(DoctorInfoSchema)
def get_current_doctor_info():
    """Get the currently authenticated doctor's info"""
    current_user = token_auth.current_user()
    CACHE_KEY  = "current_user" + current_user.get_token()
    doctor = Doctor.query.filter_by(user=current_user).first_or_404()
    qualifications_info = doctor.get_doctor_qualifications_and_info()
    doctor_info = prepare_doctor_info(doctor, qualifications_info)
    cache.set(CACHE_KEY, DoctorInfoSchema().dump(doctor_info))
    return doctor_info

@doctor.route("/all", methods=["GET"])
@authenticate(token_auth)
@cache.cached(timeout=0, key_prefix="registered_doctors", forced_update=does_doctor_cache_needs_update)
@response(DoctorInfoSchema(many=True))
def get_all():
    """Returns all the registered doctors"""
    doctors_info = []
    doctors = Doctor.query.all()
    for doctor in doctors:
        qualifications_info = doctor.get_doctor_qualifications_and_info()
        doctor_info = prepare_doctor_info(doctor, qualifications_info)
        doctors_info.append(doctor_info)
    return doctors_info

@doctor.route("/popular/doctors", methods=["GET"])
@authenticate(token_auth)
@cache.cached(timeout=10000, key_prefix="popular_doctors")
@response(DoctorInfoSchema(many=True))
def get_popular_doctors():
    import random
    """Returns all the popular doctors"""
    doctors_info = []
    doctors = Doctor.query.all()
    for doctor in doctors:
        qualifications_info = doctor.get_doctor_qualifications_and_info()
        doctor_info = prepare_doctor_info(doctor, qualifications_info)
        doctors_info.append(doctor_info)
    sample_length = ceil(0.1 * len(doctors_info))
    return random.sample(doctors_info, sample_length)

@doctor.route("/get/<int:id>", methods=["GET"])
@authenticate(token_auth)
@cache_response_with_id(prefix="doctor_id")
@response(DoctorInfoSchema())
@other_responses({404: "Doctor not found"})
def get_doctor(id):
    """Get doctor by the id"""
    CACHE_KEY = "doctor_id" + str(id)
    doctor = Doctor.query.get_or_404(id)
    qualifications_info = doctor.get_doctor_qualifications_and_info()
    doctor_info = prepare_doctor_info(doctor, qualifications_info)
    cache.set((CACHE_KEY), DoctorInfoSchema().dump(doctor_info))
    return doctor_info

@doctor.route("/add_specializations", methods=["POST"])
@authenticate(token_auth)
@body(DoctorSpecializations)
@response(DoctorSpecializations, 200)
def add_specializations(specializations):
    """Add specializations"""
    current_user = token_auth.current_user()
    doctor = current_user.doctor
    if doctor == []:
        abort(401)
    doctor = doctor[0]
    for specialization in specializations.values():
        specialization = specialization[0]
        specialization_db = Specialization.query.filter_by(name=specialization.lower()).first()
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
    doctor = current_user.doctor
    if doctor == []:
        abort(401)
    doctor = doctor[0]
    qualification_name, procurement_year, institute_name = parse_qualification_body(qualifications)
    for i in range(len(qualification_name)):
        name = qualification_name[i].lower()
        year = procurement_year[i]
        ins_name = institute_name[i].lower()
        qualification_db = Qualification.query.filter_by(name=name).first()
        doctor.add_qualification(qualification_db, year, ins_name)
    db.session.commit()
    return qualifications

@doctor.route("/add_slot", methods=["POST"])
@authenticate(token_auth)
@body(CreateNewSlot)
@response(ReturnSlot, 200)
def create_slot(kwargs):
    """Create your available slots"""
    current_user = token_auth.current_user()
    doctor = current_user.doctor
    if doctor is None:
        abort(401)
    # Fetching day from the db
    end = calculate_end_time(kwargs["start"], kwargs["appointment_duration"], kwargs["num_slots"])
    slot = Slot(**kwargs)
    slot.end = end
    slot.doctor_id = doctor[0].id
    db.session.add(slot)
    # Add event and meta details about the event
    # Also adds the booked_slot table to keep track of the slots
    create_event(slot)
    db.session.commit()
    return slot

@doctor.route("/timings/<int:id>")
@authenticate(token_auth)
@cache_response_with_id(prefix="doctor_sitting_date")
@response(TimingsSchema(many=True))
def get_doctors_next_sitting_date(id):
    """Return all the doctor's next sitting date with the given id"""
    CACHE_KEY = "doctor_sitting_date" + str(id)
    doctor = Doctor.query.get_or_404(id)
    slots = doctor.slots
    response = []
    for slot in slots:
        event = slot.get_latest_event()
        occurring_date = event.occurring_date
        # Getting number of slots booked til now 
        slots_booked = event.get_latest_event_info().slots_booked
        response.append({"slot": slot, "occurring_date": occurring_date, "slots_booked": slots_booked})
    cache.set(CACHE_KEY, TimingsSchema(many=True).dump(response))
    return response

@doctor.route("/slot/<int:id>")
@authenticate(token_auth)
@cache_response_with_id(prefix="doctor_slots")
@response(ReturnSlot(many=True))
def get_available_slots(id):
    """Return all the available slots of the doctor with the given id"""
    CACHE_KEY = "doctor_slots" + str(id)
    doctor = Doctor.query.get_or_404(id)
    response = doctor.slots
    cache.set(CACHE_KEY, ReturnSlot(many=True).dump(response))
    return response

@doctor.route("/patients", methods=["GET"])
@authenticate(token_auth)
@cache_response_with_token(prefix="doctor_patients", token=token_auth)
@response(PatientSchema(many=True))
def get_all_patients():
    """Returns all of your patients"""
    current_user = token_auth.current_user()
    doctor = current_user.doctor
    if doctor == []:
        abort(401)
    CACHE_KEY = "doctor_patients" + current_user.get_token()
    slots = doctor[0].slots
    patients = []
    for slot in slots:
        appointments = slot.appointment
        for appointment in appointments:
            patient = Patient.query.filter_by(id=appointment.patient_id).first()
            patients.append(patient)
    cache.set(CACHE_KEY, PatientSchema(many=True).dump(patients))
    return patients

@doctor.route("/patients/<int:id>")
@authenticate(token_auth)
@response(PatientSchema(many=True))
def get_appointment_patients(id):
    """Returns all the patients of the particular appointment id of the currently authenticated doctor"""
    current_user = token_auth.current_user()
    doctor = current_user.doctor
    if doctor == []:
        abort(401)
    # Verifying the appointment id belongs to the current doctor
    CACHE_KEY = "doctor_appointments" + current_user.get_token()
    slots = doctor[0].slots
    appointments = []
    for slot in slots:
        apppointments = slot.appointment
    given_appointment = Appointment.query.get(id)
    if  given_appointment not in appointments:
        abort(401)
    # Returning the list of patients
    patients = appointment.patient
    cache.set(CACHE_KEY, PatientSchema(many=True).dump(patients))
    return patients