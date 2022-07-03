from api.models import (Doctor, User, Specialization, Qualification, doctor_qualifications, Slot, Day,
                        Event, EventMeta, BookedSlots, Appointment)    
from api import db, basic_auth, token_auth
from apifairy import response, other_responses, body, authenticate
from api.doctor import doctor
from api.doctor.schema import (CreateNewDoctorSchema, DoctorSchema, doctors_schema, 
    DoctorQualifications, DoctorSpecializations, DoctorInfoSchema, CreateNewSlot, ReturnSlot, TimingsSchema)
from datetime import timedelta, date, datetime, time
from api.commands.jobs import next_weekday
from api.patient.schema import PatientSchema
from flask import abort, request, jsonify, url_for
from api.doctor.utils import get_experience, generate_hex_name, save_picture, delete_picture
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = '/path/to/the/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_url(filename="default_doctor_img.jpg"):
    return url_for("static", filename="doctor_profile_pics/"+filename, _external=True)

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
    if image != "default_doctor_image.jpg":
        delete_picture(old_image)
    doctor.image = filename
    db.session.commit()
    return jsonify({"message": "profile picture changed"})
        
@doctor.route("/info", methods=["GET"])
@authenticate(token_auth)
@response(DoctorInfoSchema)
def get_current_doctor_info():
    """Get the currently authenticated doctor's info"""
    current_user = token_auth.current_user()
    doctor = Doctor.query.filter_by(user=current_user).first_or_404()
    print(doctor)
    qualifications_info = doctor.get_doctor_qualifications_and_info()
    print(qualifications_info)
    doctor_info = prepare_doctor_info(doctor, qualifications_info)
    return doctor_info

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

@doctor.route("/all", methods=["GET"])
@authenticate(token_auth)
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

@doctor.route("/get/<int:id>", methods=["GET"])
@authenticate(token_auth)
@response(DoctorInfoSchema())
@other_responses({404: "Doctor not found"})
def get_doctor(id):
    """Get doctor by the id"""
    doctor = Doctor.query.get_or_404(id)
    qualifications_info = doctor.get_doctor_qualifications_and_info()
    doctor_info = prepare_doctor_info(doctor, qualifications_info)
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

def parse_qualification_body(qualification_body):
    qualifications = qualification_body["qualification_name"]
    procurement_year = qualification_body["procurement_year"]
    institute_name = qualification_body["institute_name"]
    return qualifications, procurement_year, institute_name

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

def calculate_end_time(start, duration, slots):
    diff = duration * slots
    # Additional 20 minutes are added to avoid clash
    end = datetime.combine(date.today(), start) + timedelta(minutes=diff+20)
    return end.time()

def create_event(slot):
    weekday = slot.day.id
    occurring_date = next_weekday(datetime.now().date(), weekday)
    event = Event(occurring_date=occurring_date, slot=slot)
    db.session.add(event)
    create_event_meta(event)
    booked_slots = BookedSlots(event=event)
    db.session.add(booked_slots)

def create_event_meta(event):
    # Interval is choosen as 7
    REPEAT_INTERVAL = 7 
    start_date = event.occurring_date
    event_meta = EventMeta(start_date=start_date, repeat_interval=REPEAT_INTERVAL, event=event)
    db.session.add(event_meta)

@doctor.route("/timings/<int:doctor_id>")
@authenticate(token_auth)
@response(TimingsSchema(many=True))
def get_doctors_next_sitting_date(doctor_id):
    """Return all the doctor's next sitting date with the given id"""
    doctor = Doctor.query.get_or_404(doctor_id)
    slots = doctor.slots
    response = []
    for slot in slots:
        event = slot.get_latest_event()
        occurring_date = event.occurring_date
        # Getting number of slots booked til now 
        slots_booked = event.get_latest_event_info().slots_booked
        response.append({"slot": slot, "occurring_date": occurring_date, "slots_booked": slots_booked})
    return response

@doctor.route("/slot/<int:doctor_id>")
@authenticate(token_auth)
@response(ReturnSlot(many=True))
def get_available_slots(doctor_id):
    """Return all the available slots of the doctor with the given id"""
    doctor = Doctor.query.get_or_404(doctor_id)
    return doctor.slots

@doctor.route("/patients", methods=["GET"])
@authenticate(token_auth)
@response(PatientSchema(many=True))
def get_all_patients():
    """Returns all of your patients"""
    current_user = token_auth.current_user()
    doctor = current_user.doctor
    if doctor == []:
        abort(401)
    slots = doctor[0].slots
    patients = []
    for slot in slots:
        appointments = slot.appointment
        for appointment in appointments:
            patient = Patient.query.filter_by(appointment-appointment).first()
            patients.append(patient)
    return patients
            
@doctor.route("/patients/<int:appointment_id>")
@authenticate(token_auth)
@response(PatientSchema(many=True))
def get_appointment_patients(appointment_id):
    """Returns all the patients of the particular appointment id of the currently authenticated doctor"""
    current_user = token_auth.current_user()
    doctor = current_user.doctor
    if doctor == []:
        abort(401)
    # Verifying the appointment id belongs to the current doctor
    slots = doctor[0].slots
    appointments = []
    for slot in slots:
        apppointments = slot.appointment
    given_appointment = Appointment.query.get(appointment_id)
    if  given_appointment not in appointments:
        abort(401)
    # Returning the list of patients
    patients = appointment.patient
    return patients