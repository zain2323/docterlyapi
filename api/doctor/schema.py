from distutils.command.config import dump_file
from api import ma, token_auth
from api.models import Doctor, User, Specialization, Qualification, Slot, Role, Day
from marshmallow import validate, validates, ValidationError, fields, post_load, post_dump, INCLUDE
from api.webadmin.schema import SpecializationSchema, QualificationSchema
from api.user.schema import UserSchema

class DoctorSpecializations(ma.Schema):
    class Meta: 
        description = 'This schema represents doctor specializations.'
    specialization_name = fields.List(fields.String(required=True, validate=[validate.Length(max=30)]))

    @validates("specialization_name")
    def validate_specialization_name(self, value):
        for specialization in value:
            specialization_db = Specialization.query.filter_by(name=specialization.lower()).first()
            if not specialization_db:
                message = f"{specialization} is an invalid choice"
                raise ValidationError(message)

class DoctorQualifications(ma.Schema):
    class Meta:
        ordered = True
        description = 'This schema represents doctor qualifications.'
    qualification_name = fields.List(fields.String(required=True, validate=[validate.Length(max=30)]))
    procurement_year = fields.List(fields.Date(required=True))
    institute_name = fields.List(fields.String(required=True))

    @validates("qualification_name")
    def validate_qualification_name(self, value):
        for qualification in value:
            qualification_db = Qualification.query.filter_by(name=qualification.lower()).first()
            if not qualification_db:
                message = f"{qualification} is an invalid choice"
                raise ValidationError(message)
    

class CreateNewDoctorSchema(ma.SQLAlchemySchema):
    class Meta:
        ordered = True
        description = 'This schema represents the attributes when registering as a doctor.'
    name = ma.String(required=True, validate=[validate.Length(min=3, max=64)])
    email = ma.String(required=True, validate=[validate.Length(max=120), validate.Email()])
    password = ma.String(reqired=True, validate=validate.Length(min=8), load_only=True)
    # dob = ma.Date(required=True)
    registered_at = ma.DateTime(dump_only=True)
    # gender = ma.String(required=True, validate=[validate.Length(max=8)])
    role = ma.String(required=True)
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
    
    @validates("role")
    def validate_role(self, value):
        role = Role.query.filter_by(role_name=value.lower()).first()
        if role is None:
            raise ValidationError("Invalid choice")
    
    @post_load
    def transform_role(self, data, **kwargs):
        data["role"] = Role.query.filter_by(role_name=data["role"]).first()
        return data

class DoctorSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Doctor
        ordered = True
        description = "This schema represents the attributes of the doctor"
    id = ma.auto_field(dump_only=True)
    user = fields.Nested(UserSchema())
    description = ma.auto_field(required=True, dump_only=True)
    specializations = fields.Nested(SpecializationSchema(many=True))
    qualifications = fields.Nested(DoctorQualifications(many=True))
    image = ma.Url(dump_only=True)

    @post_dump(pass_many=True)
    def wrap_with_dict(self, data, many, **kwargs):
        if type(data) is list:
            return {"data": data}
        else:
            return data

class CreateNewSlot(ma.Schema):
    class Meta:
        ordered = True
        description = "This schema represents the attributes required when creating slot"
    day = ma.String(required=True)
    start = ma.Time(required=True)
    end = ma.Time(format="%H:%M", dump_only=True)
    consultation_fee = ma.Integer(required=True, validate=[validate.Range(min=1)])
    appointment_duration = ma.Integer(required=True, validate=[validate.Range(min=10, max=30)])
    num_slots = ma.Integer(required=True, validate=[validate.Range(min=10, max=50)])

    @validates("day")
    def validate_day(self, value):
        day = Day.query.filter_by(name=value.lower()).first()
        if day is None:
            raise ValidationError("Invalid choice")
    
    @post_load   
    def transform_day(self, data, **kwargs):
        data["day"] = Day.query.filter_by(name=data["day"].lower()).first()
        return data

class ReturnSlot(ma.Schema):
    class Meta:
        ordered = True
        description = "This schema represents the attributes when slot is returned" 
    id = ma.Integer()
    day = ma.String()
    start = ma.Time(format="%H:%M")
    end = ma.Time(format="%H:%M")
    consultation_fee = ma.Integer()
    appointment_duration = ma.Integer()
    num_slots = ma.Integer()

    @post_dump(pass_many=True)
    def wrap_with_dict(self, data, many, **kwargs):
        if type(data) is list:
            return {"slot_data": data}
        else:
            return data

doctors_schema = DoctorSchema(many=True)

class DoctorInfoSchema(ma.Schema):
    class Meta:
        ordered = True
        unknown = INCLUDE
        description = "This schema represents the doctors information"
    id = ma.Integer()
    user = fields.Nested(UserSchema())
    description = ma.String()
    image = ma.Url()
    experience = ma.Integer()
    rating = ma.Float()
    no_of_patients = ma.Integer()
    specializations = fields.Nested(SpecializationSchema())
    qualifications = fields.Nested(DoctorQualifications())
    slot = fields.Nested(ReturnSlot(many=True))

    @post_dump(pass_many=True)
    def wrap_with_dict(self, data, many, **kwargs):
        if type(data) is list:
            return {"data": data}
        else:
            return data

class TimingsSchema(ma.Schema):
    class Meta:
        ordered = True
        description = "This schema represents the attributes of the available timings"
    slot = fields.Nested(ReturnSlot())
    occurring_date = ma.Date()
    slots_booked = ma.Integer()

    @post_dump(pass_many=True)
    def wrap_with_dict(self, data, many, **kwargs):
        if type(data) is list:
            return {"data": data}
        else:
            return data