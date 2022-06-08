from api import ma, token_auth
from marshmallow import validate, validates, ValidationError, fields
from api.models import Patient, Doctor
from api.user.schema import UserSchema

class PatientSchema(ma.SQLAlchemyAutoSchema):
    """Schema defining the attributes of the patient"""
    class Meta:
        model = Patient
        ordered = True
        exclude = ("user_id",)
    id = ma.auto_field(dump_only=True)
    user_id = ma.auto_field(required=True, dump_only=True)
    name = ma.auto_field(required=True, validate=[validate.Length(max=30)])
    dob = ma.auto_field(required=True)
    gender = ma.auto_field(required=True, validate=[validate.Length(max=8)])
    user = fields.Nested(UserSchema, dump_only=True)

    @validates("name")
    def validate_name(self, value):
        if not value[0].isalpha():
            raise ValidationError("Email must start with a letter")
    
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

patients_schema = PatientSchema(many=True)
    
    