import base64
import os
from api import db, login_manager
from datetime import datetime, timedelta
from werkzeug.security import check_password_hash, generate_password_hash
from collections import OrderedDict
from flask_login.mixins import UserMixin

doctor_specializations = db.Table("doctor_specializations",
    db.Column('doctor_id', db.Integer, db.ForeignKey('doctor.id', ondelete='CASCADE'), primary_key=True, nullable=False),
    db.Column('specialization_id', db.Integer, db.ForeignKey('specialization.id', ondelete="RESTRICT"), primary_key=True, nullable=False)
)

doctor_qualifications = db.Table("doctor_qualfications",
    db.Column('doctor_id', db.Integer, db.ForeignKey('doctor.id', ondelete='CASCADE'), primary_key=True, nullable=False),
    db.Column('qualification_id', db.Integer, db.ForeignKey('qualification.id', ondelete="RESTRICT"), primary_key=True, nullable=False),
    db.Column('procurement_year', db.Date, nullable=False),
    db.Column('institute_name', db.String, nullable=False)

)

medical_history = db.Table("medical_history",
    db.Column("patient_id", db.Integer, db.ForeignKey("patient.id", ondelete="CASCADE"), primary_key=True, nullable=False),
    db.Column("prescription_id", db.Integer, db.ForeignKey("prescription.id", ondelete="CASCADE"), primary_key=True, nullable=False)
)

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
    name = db.Column(db.String(30), unique=True, nullable=False, index=True)

    def __repr__(self):
        return f"{self.name}"

class Qualification(db.Model):
    __tablename__= "qualification"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True, index=True, nullable=False)

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
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password = db.Column(db.String(60), nullable=False)
    registered_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    confirmed = db.Column(db.Boolean, default=False, nullable=False)
    dob = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(8), nullable=False)
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

    def get_token(self, expires_in=3600):
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
        if user is None or user.token != token or user.token_expiration < datetime.utcnow():
            return None
        return user
    
    def __repr__(self):
        return f"{self.name}, {self.email}"
    
class Doctor(db.Model):
    __tablename__ = "doctor"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    description = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
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
    
    def get_specializations(self):
        return self.specializations.all()
    
    def get_qualifications(self):
        return self.qualifications.all()
    
    def get_user(self):
        return self.user
    
    def add_specialization(self, specialization):
        self.specializations.append(specialization)
    
    def add_qualification(self, qualification, procurement_year, institute_name):
        statement = doctor_qualifications.insert().values(doctor_id=self.id, qualification_id=qualification.id,
                procurement_year=procurement_year, institute_name=institute_name)
        db.session.execute(statement)
    
    def get_doctor_qualifications_and_info(self):
        query = db.select(doctor_qualifications.c.institute_name, doctor_qualifications.c.procurement_year)
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

class Prescription(db.Model):
    __tablename__ = "prescription"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    appointment_id = db.Column(db.Integer, db.ForeignKey("appointment.id"), nullable=False)
    description = db.Column(db.String, nullable=False)
    prescribed_medicines = db.relationship("PrescribedMedicines", backref="prescription", lazy=True)

    def __repr__(self):
        return f"appointment_id: {self.appointment_id}, description: {self.description}"

class Patient(db.Model):
    __tablename__ = "patient"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    name = db.Column(db.String(30), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(8), nullable=False)
    rating = db.relationship("Rating", backref="patient", lazy=True)
    appointment = db.relationship("Appointment", backref="patient", lazy=True)
    history = db.relationship(
        "Prescription", secondary=medical_history,
        primaryjoin=(medical_history.c.patient_id == id),
        secondaryjoin = (medical_history.c.prescription_id == Prescription.id),
        backref=db.backref("patient", lazy="dynamic", cascade="all, delete")
    )
    
    def __repr__(self):
        return f"Name: {self.name}"

class Rating(db.Model):
    __tablename__ = "rating"
    __table_args__ = (
        db.CheckConstraint("rating < 6"),
    )
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctor.id"), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey("patient.id"), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    review = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f"'Doctor Id: {self.doctor_id}, Patient Id: {self.patient_id}, Rating: {self.rating}, Review: {self.review}"

class Appointment(db.Model):
    __tablename__ = "appointment"
    __table_args__ = (
        db.UniqueConstraint('slot_id', 'patient_id', name="unique_appointment"),
    )
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    slot_id = db.Column(db.Integer, db.ForeignKey('slot.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    prescription = db.relationship("Prescription", backref="appointment", lazy=True)

    def __repr__(self):
        return f"slot_id: {self.slot_id}, patient_id:{self.patient_id}, date:{self.date}"

class Slot(db.Model):
    __tablename__ = "slot"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    day_id = db.Column(db.Integer, db.ForeignKey('day.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctor.id"), nullable=False)
    start = db.Column(db.Time, nullable=False)
    end = db.Column(db.Time, nullable=False)
    consultation_fee = db.Column(db.Integer, nullable=False)
    appointment_duration = db.Column(db.Integer, nullable=False)
    num_slots = db.Column(db.Integer, nullable=False)
    appointment = db.relationship("Appointment", backref="slot", lazy=True)
    
    def __repr__(self):
        return f"Start: {self.start}, End: {self.end}"

class PrescribedMedicines(db.Model):
    __tablename = "prescribed_medicine"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    prescription_id = db.Column(db.Integer, db.ForeignKey("prescription.id"), nullable=False)
    medicine_name = db.Column(db.String, nullable=False)
    medicine_formula = db.Column(db.String, nullable=False)
    dosage = db.Column(db.String, nullable=False)
    brand = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f"Medicine: {self.medicine_name}, Dosage: {self.dosage}"