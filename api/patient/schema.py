from api import ma, token_auth
from marshmallow import validate, validates, ValidationError, fields,validates_schema, post_dump
from api.models import Patient, Doctor, Event, Slot, Appointment
from api.user.schema import UserSchema
from api.doctor.schema import ReturnSlot, TimingsSchema, DoctorInfoSchema

class PatientSchema(ma.SQLAlchemyAutoSchema):
    """Schema defining the attributes of the patient"""
    class Meta:
        model = Patient
        ordered = True
        exclude = ("user_id",)
    id = ma.auto_field(dump_only=True)
    user_id = ma.auto_field(required=True, dump_only=True)
    name = ma.auto_field(required=True, validate=[validate.Length(max=30)])
    age = ma.auto_field(required=True)
    gender = ma.auto_field(required=True, validate=[validate.Length(max=8)])
    user = fields.Nested(UserSchema, dump_only=True)

    @post_dump(pass_many=True)
    def wrap_with_dict(self, data, many, **kwargs):
        if type(data) is list:
            return {"data": data}
        else:
            return data

    @validates("name")
    def validate_name(self, value):
        if not value[0].isalpha():
            raise ValidationError("Email must start with a letter")
    
    @validates("gender")
    def validate_gender(self, value):
        value = value.lower()
        if value not in ["male", "female"]:
            raise ValidationError("Invalid gender")
    
    @validates("user_id")
    def validate_user(self, value):
        """Get the id of the currently authenticated user and check if the given id is equal to that"""
        current_user = token_auth.current_user()
        db_user = User.query.get(value)
        if db_user is None or current_user.id != value:
            raise ValidationError("Invalid user id provided")
        # Checking if the currently authenticated user is not doctor
        doctor = Doctor.query.filter_by(user_id=current_user.id)
        if doctor:
            raise ValidationError("Doctor is not allowed to register as a patient")
    
    @validates("age")
    def validate_age(self, value):
        if value < 0:
            raise ValidationError("Age must be positive.")

class AppointmentSchema(ma.Schema):
    class Meta:
        ordered = True
    id = ma.Integer(dump_only=True)
    slot_id = ma.Integer(required=True)
    patient_id = ma.Integer(required=True)

    @validates("patient_id")
    def validate_patient_id(self, value):
        current_user = token_auth.current_user()
        patient = Patient.query.get(value)
        if patient is None:
            raise ValidationError("Invalid patient provided!")
        current_user_patients = current_user.patient
        if not patient in current_user_patients:
            raise ValidationError("Authorization Error. The patient your are trying to register either does not exist or does not belong to you.")

    @validates("slot_id")
    def validate_slot_id(self, value):
        slot = Slot.query.get(value)
        if slot is None:
            raise ValidationError("Invalid slot provided!")
        slots_booked = slot.get_latest_event().get_latest_event_info().slots_booked
        if slots_booked >= slot.num_slots:
            raise ValidationError("All slots are full!")
    
    @validates_schema
    def validate_unique_patient_per_event(self, data, **kwargs):
        patient_id = data["patient_id"]
        slot_id = data["slot_id"]
        # Getting patient and slot objects from their respective ids
        patient = Patient.query.get(patient_id)
        slot = Slot.query.get(slot_id)
        # Verifying if the slot and patient exists
        if slot is None or patient is None:
            raise ValidationError("Either patient or slot does not exist.")
        # Getting the event object from the slot
        event = slot.get_latest_event()
        # Checking if there exists an appoinment
        appointment = Appointment.query.filter_by(event=event, slot=slot, patient=patient).first()
        if appointment is not None:
            raise ValidationError("You have already registered a slot for the patient named " + patient.name)

class ReturnAppointmentSchema(ma.Schema):
    class Meta:
        ordered = True
    id = ma.Integer()
    patient = fields.Nested(PatientSchema())
    timings = fields.Nested(TimingsSchema())
    expected_time = ma.Time()

class AppointmentHistorySchema(ma.Schema):
    class Meta:
        ordered = True
    id = ma.Integer()
    patient = fields.Nested(PatientSchema())
    doctor = fields.Nested(DoctorInfoSchema())
    timings = fields.Nested(TimingsSchema())

    @post_dump(pass_many=True)
    def wrap_with_dict(self, data, many, **kwargs):
        if type(data) is list:
            return {"data": data}
        else:
            return data

patients_schema = PatientSchema(many=True)
    
    