from datetime import datetime, date, timedelta
from pathlib import Path
import secrets
from PIL import Image
from api import db
from flask import url_for
from api.commands.jobs import next_weekday
from api.models import Event, EventMeta, BookedSlots

IS_DOCTOR_CACHE_NEEDS_TO_UPDATE = False
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_url(filename="default_doctor_img.jpg"):
    return url_for("static", filename="doctor_profile_pics/"+filename, _external=True)

def parse_qualification_body(qualification_body):
    qualifications = qualification_body["qualification_name"]
    procurement_year = qualification_body["procurement_year"]
    institute_name = qualification_body["institute_name"]
    return qualifications, procurement_year, institute_name

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

def get_experience(qualifications):
    # Returns the experience of the doctor by subracting the earliest date of degree procurement from the current date
    date_format = "%Y-%m-%d"
    try:
        min_date = str(min(qualifications["procurement_year"]))
    except:
        min_date = str(datetime.now().date())
    current_date = str(datetime.now().date())

    min_date = datetime.strptime(min_date, date_format)
    current_date = datetime.strptime(current_date, date_format)

    return int((abs(current_date - min_date).days)/365)

def save_picture(image_data, img_name, loc='./api/static/doctor_profile_pics'):
    '''
    This saves the thumbnail picture of the product in the static/product_pictures directory.
    Picture is being renamed  to the randomly chosen 32 bit string in order to avoid the
    naming clash.
    '''
    try:
        path = Path(loc)
    except FileNotFoundError:
        raise FileNotFoundError("Path is invalid or does not exist.")
    try:
        _, ext = image_data.filename.split(".")
    except:
        ext = image_data.filename.split(".")[-1]
    image_name_with_ext = img_name + "." + ext
    path = path.joinpath(image_name_with_ext)
    try:
        i = Image.open(image_data)
    except FileNotFoundError:
        raise Exception(f"File {image_data} not found at the given path.")
    i = i.resize((500,375))
    i.save(path)
    return image_name_with_ext

def delete_picture(img_name, loc="./api/static/doctor_profile_pics/"):
    try:
        path = Path(loc + img_name)
    except FileNotFoundError:
        raise FileNotFoundError("Path is invalid or does not exist.")
    if path.exists():
        path.unlink()

def generate_hex_name():
    '''
    Returns the 32 bit random digits
    '''
    return secrets.token_hex(32)

def get_patient_count(doctor):
    id = doctor.id
    query = f"""SELECT COUNT(*) FROM doctor d JOIN "user" u ON u.id = d.user_id JOIN slot s ON s.doctor_id = d.id JOIN appointment a On a.slot_id = s.id WHERE d.id = {id};"""
    return db.session.execute(query).all()[0][0]

# Does cached list of doctor needs to update?
def does_doctor_cache_needs_update():
    try:
        IS_DOCTOR_CACHE_NEEDS_TO_UPDATE
    except:
        IS_DOCTOR_CACHE_NEEDS_TO_UPDATE = False
    if IS_DOCTOR_CACHE_NEEDS_TO_UPDATE:
        IS_DOCTOR_CACHE_NEEDS_TO_UPDATE = False
        return True
    return False

def update_doctor_cache(update=False):
    IS_DOCTOR_CACHE_NEEDS_TO_UPDATE = update

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