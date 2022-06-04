from distutils.command.config import dump_file
from telnetlib import DO
from api import ma, token_auth
from api.models import Doctor, User
from marshmallow import validate, validates, ValidationError

class CreateNewDoctorSchema(ma.SQLAlchemySchema):
    """Scema defining the attributes when registering as a doctor"""
    class Meta:
        ordered = True

    name = ma.String(required=True, validate=[validate.Length(min=3, max=64)])
    email = ma.String(required=True, validate=[validate.Length(max=120), validate.Email()])
    password = ma.String(reqired=True, validate=validate.Length(min=8), load_only=True)
    dob = ma.Date(required=True)
    gender = ma.String(required=True, validate=[validate.Length(max=8)])
    role_id = ma.Integer(required=True)
    description = ma.String(required=True)

    @validates("email")
    def validate_email(self, value):
        if not value[0].isalpha():
            raise ValidationError("Email must start with a letter")
        user = token_auth.current_user()
        db_user = User.query.filter_by(email=value).first()
        if db_user and user is None:
            raise ValidationError("This email is already in use")
        if db_user and db_user.id != user.id:
            raise ValidationError("This email is already in use")
    
    @validates("name")
    def validate_name(self, value):
        if not value[0].isalpha():
            raise ValidationError("Email must start with a letter")

class DoctorSchema(ma.SQLAlchemySchema):
    """Schema defining the attributes of the doctor"""
    class Meta:
        ordered = True
    name = ma.String()
    email = ma.String()
    dob = ma.String()
    gender = ma.String()
    rating = ma.Integer()
    description = ma.String()
    specialization = ma.List()
    qualfications = ma.List()
