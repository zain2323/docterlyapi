from api.commands import commands
from api.models import Doctor, Slot, BookedSlots, Event, EventMeta, User, Role, Day, Specialization, Qualification
from datetime import datetime, timedelta
from api import db, api_fairy
from json import dumps
from flask import current_app
from faker import Faker

@commands.cli.command()
def create_scheduled_events():
    """Create events for the doctor's slot"""
    slots = Slot.query.all()
    for slot in slots:
        # get day. start and end time
        day = slot.day
        start = slot.start
        end = slot.end
        # Getting next date of the appointment
        current_date = datetime.now().date()
        current_time = datetime.now().time()
        next_date = next_weekday(current_date, day.id)
        # Fetching current date of the appointment
        event = slot.get_latest_event()
        current_occurring_date = event.occurring_date
        # If the current date is equal to the next date then we only need to create new event when there is some time left.
        # If they are not equal and the next date is greater than the current date, then this means
        # we need to create new event    
        # or (current_occurring_date == next_date and end < current_time)
        if (current_occurring_date < next_date):
            # Fetch the current event meta
            event_meta = event.get_event_meta()
            interval = event_meta.repeat_interval
            start_date = event_meta.start_date
            # Generating the new date
            new_date = (current_date - start_date) + timedelta(days=interval)
            # Creating the new event
            new_event = Event(occurring_date=next_date, slot=slot)
            db.session.add(new_event)
            # Creating the event meta
            REPEAT_INTERVAL = 7 
            start_date = event.occurring_date
            event_meta = EventMeta(start_date=start_date, repeat_interval=REPEAT_INTERVAL, event=new_event)
            db.session.add(event_meta)
            # Creating the new booked slot
            new_booked_slot = BookedSlots(event=new_event)
            db.session.add(new_booked_slot)
            db.session.commit()
            print("Added event")
    print("Job executed")

def next_weekday(date, weekday):
    days_ahead = weekday - date.isoweekday()
    if days_ahead <= 0:
        days_ahead += 7
    return date + timedelta(days_ahead)   

@commands.cli.command()
def create_openapispec_file():
    with current_app.test_request_context():
        with open("openapispec.json", "w") as file:
            data = dumps(api_fairy.apispec)
            file.write(data)

@commands.cli.command()
def insert_prerequiste_data():
    """Inserts all the prerequiste data in the database"""
    insert_roles()
    create_admin_account()
    insert_days()
    insert_specializations()
    insert_qualifications()
    db.session.commit()
    print("Data inserted...")

def insert_roles():
    admin = Role(role_name="admin")
    user = Role(role_name="user")
    db.session.add(admin)
    db.session.add(user)
    db.session.commit()

def create_admin_account():
    name = "admin"
    email = "admin@admin.com"
    password = "testing123"
    confirmed = True
    # gender = "male"
    role = Role.query.filter_by(role_name="admin").first()
    # dob = datetime(2002, 5, 22)
    admin_account = User(name=name, email=email, password=password, confirmed=confirmed, role=role)
    admin_account.set_password(password)
    db.session.add(admin_account)

def insert_days():
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    for day in days:
        day_db = Day(name=day.lower())
        db.session.add(day_db)

def insert_specializations():
    specializations = ["Allergist", "Anesthesiologist", "Cardiologist", "Dermatologist", "Endocrinologist",
                       "Emergency Medicine Specialist", "Family Physician", "Critical Care Medicine Specialist",
                       "Gastroenterologist", "Geriatric Medicine Specialist", "Hematologist", "Hospice and Palliative Medicine Specialist",
                        "Infectious Disease Specialist", "Internist", "Medical Geneticist", "Nephrologist", "Neurologist",
                        "Obstetricians and Gynecologist", "Oncologist", "Ophthalmologist", "Osteopaths", "Otolaryngologist",
                        "Pathologist", "Pediatrician", "Physiatrist", "Plastic Surgeon", "Podiatrist", "Preventive Medicine Specialist",
                        "Psychiatrists", "Pulmonologist", "Radiologist", "Rheumatologist", "Sleep medicine specialist", 
                        "Sports Medicine Specialist", "General Surgeon", "Urologist"]
    for specialization in specializations:
        specialization_db = Specialization(name=specialization.lower(), image="allergist.jpg")
        db.session.add(specialization_db)

def insert_qualifications():
    qualifications = ["MBBS", "BDS", "BAMS", "BUMS", "BHMS", "BYNS", "FRCPS", "MD", "DO"]
    for qualification in qualifications:
        qualification_db = Qualification(name=qualification.lower())
        db.session.add(qualification_db)

@commands.cli.command()
def create_fake_doctors():
    fake = Faker()
    n = 100
    password = "testing123"
    image = "default_doctor_image.jpg"
    role = Role.query.filter_by(role_name="user").first()
    qualifications_list = Qualification.query.all()
    specialization_list = Specialization.query.all()
    for _ in range(n):
        qualification = fake.word(ext_word_list=qualifications_list)
        procurement_year = datetime.strptime(fake.date(), "%Y-%m-%d").date()
        institute_name = fake.word()
        specialization = fake.word(ext_word_list=specialization_list)
        name = fake.unique.name()
        email = fake.unique.email()
        description = fake.paragraph()
        # User object
        user = User(name=name, email=email, password=password, role=role)
        user.set_password(password)
        # db.session.add(user)
        # Doctor object
        doctor = Doctor(user=user, description=description, image=image)
        # db.session.add(doctor)
        # doctor.add_specialization(specialization)
        # doctor.add_qualification(qualification, procurement_year, institute_name)
        # db.session.commit()
        print(user)
        print(doctor)
        print(specialization)
        print(qualification)

@commands.cli.command()
def testing_job():
    import time
    print("Starting date is", datetime.now())
    print("Sleeping for 5 seconds")
    time.sleep(5)
    print("Task executed..")
    print("Ending date is", datetime.now())

@commands.cli.command()
def backup_database():
    import os
    filename = f'{datetime.now().date()}_dumpfile'
    pwd = current_app.config["PGPASSWORD"]
    cmd = f'''PGPASSWORD={pwd} pg_dump -U postgres -d doctorly_db > /home/zain2323/docterlyapi/db_dump/{filename}'''
    os.system(cmd)
    print("executed")