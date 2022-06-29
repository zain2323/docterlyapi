from api import ma
from marshmallow import validate, validates, ValidationError
from api.models import Specialization, Qualification, Role

class QualificationSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Qualification
        ordered = True
    id = ma.auto_field(dump_only=True)
    name = ma.auto_field(required=True, validate=[validate.Length(max=50)])

class SpecializationSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Specialization
        ordered = True
    id = ma.auto_field(dump_only=True)
    name = ma.auto_field(required=True, validate=[validate.Length(max=50)])

class RoleSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Role
        ordered = True
    id = ma.auto_field(dump_only=True)
    role_name = ma.auto_field(required=True, validate=[validate.Length(max=20)], dump_only=True)

