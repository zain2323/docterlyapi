from distutils.command.config import dump_file
from api import ma, token_auth
from api.models import Doctor, User
from marshmallow import validate, validates, ValidationError, fields
from api.webadmin.schema import SpecializationSchema, QualificationSchema
from api.user.schema import UserSchema


class CreateNewDoctorSchema(ma.SQLAlchemySchema):
    """Schema defining the attributes when registering as a doctor"""
    class Meta:
        ordered = True
    name = ma.String(required=True, validate=[validate.Length(min=3, max=64)])
    email = ma.String(required=True, validate=[validate.Length(max=120), validate.Email()])
    password = ma.String(reqired=True, validate=validate.Length(min=8), load_only=True)
    dob = ma.Date(required=True)
    registered_at = ma.DateTime(dump_only=True)
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

class DoctorSchema(ma.SQLAlchemyAutoSchema):
    """Schema defining the attributes of the doctor"""
    class Meta:
        model = Doctor
        ordered = True
    id = ma.auto_field(dump_only=True)
    user = fields.Nested(UserSchema())
    description = ma.auto_field(required=True, dump_only=True)
    specializations = fields.Nested(SpecializationSchema())
    qualifications = fields.Nested(QualificationSchema())