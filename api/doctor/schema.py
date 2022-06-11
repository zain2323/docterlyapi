from distutils.command.config import dump_file
from api import ma, token_auth
from api.models import Doctor, User, Specialization, Qualification
from marshmallow import validate, validates, ValidationError, fields
from api.webadmin.schema import SpecializationSchema, QualificationSchema
from api.user.schema import UserSchema

class DoctorSpecializations(ma.Schema):
    specialization_name = fields.List(fields.String(required=True, validate=[validate.Length(max=30)]))

    @validates("specialization_name")
    def validate_specialization_name(self, value):
        for specialization in value:
            print(specialization)
            specialization_db = Specialization.query.filter_by(name=specialization).first()
            if not specialization_db:
                message = f"{specialization} is an invalid choice"
                raise ValidationError(message)

class DoctorQualifications(ma.Schema):
    class Meta:
        ordered = True
    qualification_name = fields.List(fields.String(required=True, validate=[validate.Length(max=30)]))
    procurement_year = fields.List(fields.Date(required=True))
    institute_name = fields.List(fields.String(required=True))

    @validates("qualification_name")
    def validate_qualification_name(self, value):
        for qualification in value:
            qualification_db = Qualification.query.filter_by(name=qualification).first()
            if not qualification_db:
                message = f"{qualification} is an invalid choice"
                raise ValidationError(message)
    

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
    specializations = fields.Nested(SpecializationSchema(many=True))
    qualifications = fields.Nested(QualificationSchema(many=True))

class DoctorInfoSchema(ma.Schema):
    class Meta:
        ordered = True
    id = ma.Integer()
    user = fields.Nested(UserSchema())
    description = ma.String()
    Specialization = fields.Nested(SpecializationSchema(many=True))
    qualifications = fields.Nested(DoctorQualifications())

doctors_schema = DoctorSchema(many=True)
