import base64
import os
from api import db, login_manager, search_api
from datetime import datetime, timedelta
from werkzeug.security import check_password_hash, generate_password_hash
from collections import OrderedDict
from flask_login.mixins import UserMixin

doctor_specializations = db.Table("doctor_specializations",
    db.Column('doctor_id', db.Integer, db.ForeignKey('doctor.id', ondelete='CASCADE'), primary_key=True, nullable=False),
    db.Column('specialization_id', db.Integer, db.ForeignKey('specialization.id', ondelete="RESTRICT"), primary_key=True, nullable=False)
)

doctor_qualifications = db.Table("doctor_qualifications",
    db.Column('doctor_id', db.Integer, db.ForeignKey('doctor.id', ondelete='CASCADE'), primary_key=True, nullable=False),
    db.Column('qualification_id', db.Integer, db.ForeignKey('qualification.id', ondelete="RESTRICT"), primary_key=True, nullable=False),
    db.Column('procurement_year', db.Date, nullable=False),
    db.Column('institute_name', db.String, nullable=False)
)

# medical_history = db.Table("medical_history",
#     db.Column("patient_id", db.Integer, db.ForeignKey("patient.id", ondelete="CASCADE"), primary_key=True, nullable=False),
#     db.Column("prescription_id", db.Integer, db.ForeignKey("prescription.id", ondelete="CASCADE"), primary_key=True, nullable=False)
# )

class Role(db.Model):
    __tablename__ = "role"
    id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(20), index=True, unique=True, default="user", nullable=False)
    user = db.relationship("User", backref="role", lazy=True) 

    def __repr__(self):
        return f"{self.role_name}"

class Specialization(db.Model):
    __tablename__ = "specialization"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False, index=True)
    image = db.Column(db.String)

    def __repr__(self):
        return f"{self.name}"

class Qualification(db.Model):
    __tablename__= "qualification"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, index=True, nullable=False)

    def __repr__(self):
        return f"{self.name}"

class Day(db.Model):
    __tablename__ = "day"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(10), unique=True, nullable=False, index=True)
    slot = db.relationship("Slot", backref="day", lazy=True)

    def __repr__(self):
        return f"{self.name}"

@login_manager.user_loader
def load_user(user_id):
    return User.get_user(user_id)

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    __searchable__ = ["id", "name", "email", "password", "registered_at", "confirmed", "role"]
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password = db.Column(db.String(102), nullable=False)
    registered_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    confirmed = db.Column(db.Boolean, default=False, nullable=False)
    # dob = db.Column(db.Date, nullable=False)
    # gender = db.Column(db.String(8), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey("role.id"), nullable=False)
    token = db.Column(db.String(32), index=True, unique=True)
    token_expiration = db.Column(db.DateTime)
    doctor = db.relationship("Doctor", backref="user", lazy=True)
    patient = db.relationship("Patient", backref="user", lazy=True)
    
    @staticmethod
    def get_user(id):
        return User.query.get(id)

    def set_password(self, plain_password):
        self.password = self.generate_hashed_password(plain_password)
    
    @staticmethod
    def generate_hashed_password(plain_password):
        return generate_password_hash(plain_password)

    def verify_password(self,plain_password):
        return check_password_hash(self.password, plain_password)

    def get_token(self, expires_in=31536000):
        # token expires in a year
        now = datetime.utcnow()
        if self.token and self.token_expiration > now + timedelta(seconds=60):
            return self.token
        self.token = base64.b64encode(os.urandom(24)).decode('utf-8')
        self.token_expiration = now + timedelta(seconds=expires_in)
        db.session.add(self)
        return self.token
    
    def revoke_token(self):
        self.token_expiration = datetime.utcnow() - timedelta(seconds=1)

    @staticmethod
    def verify_token(token):
        user = User.query.filter_by(token=token).first()
        # Removed token expiration
        #  or user.token_expiration < datetime.utcnow()
        if user is None or user.token != token:
            return None
        return user
    
    def __repr__(self):
        return f"{self.name}, {self.email}"

class Doctor(db.Model):
    __tablename__ = "doctor"
    __searchable__ = ["id", "description", "image", "rating"]
    
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    description = db.Column(db.String)
    image = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), index=True)
    rating = db.relationship("Rating", backref="doctor", lazy=True)
    slots = db.relationship("Slot", backref="doctor", lazy=True)
    # Many to Many relationship between doctor and specializations
    specializations = db.relationship(
    "Specialization", secondary=doctor_specializations,
    primaryjoin=(doctor_specializations.c.doctor_id == id),
    secondaryjoin=(doctor_specializations.c.specialization_id == Specialization.id),
    backref=db.backref("doctor", lazy='dynamic'), lazy=True, cascade="all, delete")
    # Many to Many relationship between doctor and qualifications
    qualifications = db.relationship(
    "Qualification", secondary=doctor_qualifications,
    primaryjoin=(doctor_qualifications.c.doctor_id == id),
    secondaryjoin=(doctor_qualifications.c.qualification_id == Qualification.id),
    backref=db.backref("doctor", lazy='dynamic'), lazy=True, cascade="all, delete")

    def __repr__(self):
        return f"doctor:id {self.id}"
    
    def get_user(self):
        return self.user
    
    def add_specialization(self, specialization):
        self.specializations.append(specialization)
        search_api.add_to_index(self)
    
    def add_qualification(self, qualification, procurement_year, institute_name):
        statement = doctor_qualifications.insert().values(doctor_id=self.id, qualification_id=qualification.id,
                procurement_year=procurement_year, institute_name=institute_name)
        db.session.execute(statement)
        search_api.add_to_index(self)
    
    def get_doctor_qualifications_and_info(self):
        query = db.select(doctor_qualifications.c.institute_name, doctor_qualifications.c.procurement_year).filter(doctor_qualifications.c.doctor_id == self.id)
        result = db.session.execute(query).all()
        qualifications_list = self.qualifications
        procurement_year_list = []
        institute_name_list = [] 
        for info in result:
            institute_name_list.append(info[0])
            procurement_year_list.append(info[1])
        
        info_dict = {
            "qualification_name": qualifications_list,
            "procurement_year": procurement_year_list,
            "institute_name": institute_name_list
        }
        return info_dict
    
    def get_qualifications_info(self):
        query = db.select(doctor_qualifications.c.institute_name, doctor_qualifications.c.procurement_year).filter(doctor_qualifications.c.doctor_id == self.id)
        result = db.session.execute(query).all()
        qualifications_list = [str(q) for q in self.qualifications]
        procurement_year_list = []
        institute_name_list = [] 
        for info in result:
            institute_name_list.append(str(info[0]))
            procurement_year_list.append(str(info[1]))
        
        payload = {
            "qualification_name": qualifications_list,
            "procurement_year": procurement_year_list,
            "institute_name": institute_name_list
        }
        return payload

    def get_specializations_info(self):
        try:
            specialization = self.specializations[0]
            return {"id": str(specialization.id), "name": str(specialization.name)}
        except:
            return {}

# class Prescription(db.Model):
#     __tablename__ = "prescription"
#     id = db.Column(db.Integer, primary_key=True, nullable=False)
#     appointment_id = db.Column(db.Integer, db.ForeignKey("appointment.id"), nullable=False)
#     description = db.Column(db.String, nullable=False)
#     prescribed_medicines = db.relationship("PrescribedMedicines", backref="prescription", lazy=True)

#     def __repr__(self):
#         return f"appointment_id: {self.appointment_id}, description: {self.description}"

class Patient(db.Model):
    __tablename__ = "patient"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    name = db.Column(db.String(30), nullable=False, index=True)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(8), nullable=False, index=True)
    symptoms = db.Column(db.String)
    rating = db.relationship("Rating", backref="patient", lazy=True)
    appointment = db.relationship("Appointment", backref="patient", lazy=True)
    # history = db.relationship(
    #     "Prescription", secondary=medical_history,
    #     primaryjoin=(medical_history.c.patient_id == id),
    #     secondaryjoin = (medical_history.c.prescription_id == Prescription.id),
    #     backref=db.backref("patient", lazy="dynamic", cascade="all, delete")
    # )
    
    def __repr__(self):
        return f"Name: {self.name}"

class Rating(db.Model):
    __tablename__ = "rating"
    __table_args__ = (
        db.CheckConstraint("rating < 6"),
    )
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctor.id"), nullable=False, index=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patient.id"), nullable=False, index=True)
    rating = db.Column(db.Integer, nullable=False)
    review = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f"'Doctor Id: {self.doctor_id}, Patient Id: {self.patient_id}, Rating: {self.rating}, Review: {self.review}"

class Appointment(db.Model):
    __tablename__ = "appointment"
    __table_args__ = (
        db.UniqueConstraint('event_id', 'patient_id', 'slot_id', name="unique_appointment"),
    )
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    slot_id = db.Column(db.Integer, db.ForeignKey('slot.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    # prescription = db.relationship("Prescription", backref="appointment", lazy=True)

    def __repr__(self):
        return f"slot_id: {self.slot_id}, patient_id:{self.patient_id}"

class Slot(db.Model):
    __tablename__ = "slot"
    __searchable__ = ["id", "day", "start", "end", "consultation_fee", "appointment_duration", "num_slots"]
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    day_id = db.Column(db.Integer, db.ForeignKey('day.id'), nullable=False, index=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctor.id"), nullable=False, index=True)
    start = db.Column(db.Time, nullable=False)
    end = db.Column(db.Time, nullable=False)
    consultation_fee = db.Column(db.Integer, nullable=False)
    appointment_duration = db.Column(db.Integer, nullable=False)
    num_slots = db.Column(db.Integer, nullable=False)
    appointment = db.relationship("Appointment", backref="slot", lazy=True)
    event = db.relationship("Event", backref="slot", lazy=True)

    def get_latest_event(self):
        return self.event[-1]

    def __repr__(self):
        return f"Start: {self.start}, End: {self.end}"

class BookedSlots(db.Model):
    __tablename__ = "booked_slots"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    event_id = db.Column(db.ForeignKey("event.id"), nullable=False, index=True)
    slots_booked = db.Column(db.Integer, default=0)

    def increment_slot(self):
        self.slots_booked += 1

    def __repr__(self):
        return f"Slots Booked: {self.slots_booked}"

class Event(db.Model):
    __tablename__ = "event"
    __table_args__ = (
        db.UniqueConstraint('occurring_date', 'slot_id', name="unique_slot_event"),
    )
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    occurring_date = db.Column(db.Date, nullable=False)
    slot_id = db.Column(db.ForeignKey("slot.id"), nullable=False, index=True)
    event_meta = db.relationship("EventMeta", backref="event", lazy=True)
    booked_slots = db.relationship("BookedSlots", backref="event", lazy=True)
    appointment = db.relationship("Appointment", backref="event", lazy=True)

    def get_latest_event_info(self):
        return self.booked_slots[-1]

    def get_event_meta(self):
        return self.event_meta[0]

    def __repr__(self):
        return f"Occurring date: {self.occurring_date}\n Slot Id: {self.slot_id}"

class EventMeta(db.Model):
    __tablename__ = "event_meta"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey("event.id"), nullable=False, index=True)
    start_date = db.Column(db.Date, nullable=False)    
    repeat_interval = db.Column(db.Integer, nullable=False)
    
    def __repr__(self):
        return f"Event Id: {self.event_id}\n Start Date: {self.start_date}\n Repeat Interval: {self.repeat_interval}"

# WHERE ( DATEDIFF( '2022-6-7', start_date ) % repeat_interval = 0)

# class PrescribedMedicines(db.Model):
#     __tablename = "prescribed_medicine"
#     id = db.Column(db.Integer, primary_key=True, nullable=False)
#     prescription_id = db.Column(db.Integer, db.ForeignKey("prescription.id"), nullable=False)
#     medicine_name = db.Column(db.String, nullable=False)
#     medicine_formula = db.Column(db.String, nullable=False)
#     dosage = db.Column(db.String, nullable=False)
#     brand = db.Column(db.String, nullable=False)

#     def __repr__(self):
#         return f"Medicine: {self.medicine_name}, Dosage: {self.dosage}"



def after_insert_listener(mapper, connection, target):
    # 'target' is the inserted object
    if isinstance(target, Slot):
        doctor = Doctor.query.get(target.doctor_id)
        search_api.add_to_index(doctor)
    elif isinstance(target, Doctor):
        search_api.add_to_index(target)
    else: print("TARGET", target)

db.event.listen(Doctor, 'after_insert', after_insert_listener)
db.event.listen(Slot, 'after_insert', after_insert_listener)

# @db.event.listens_for(Doctor.qualifications, "append")
# def qualification_event(target, value, initiator):
#     print("I updatedsssssssssssssssssss", target.name)
