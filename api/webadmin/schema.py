from api import ma
from marshmallow import validate, validates, ValidationError, post_dump
from api.models import Specialization, Qualification, Role
from flask import url_for

def generate_url(filename="allergist.jpg"):
    return url_for("static", filename="specialization_images/"+filename, _external=True)

class QualificationSchema(ma.Schema):
    class Meta:
        ordered = True
        description = "This schema represents the attributes of the qualification"
    id = ma.Integer()
    name = ma.String(required=True, validate=[validate.Length(max=50)])
    
    @post_dump(pass_many=True)
    def wrap_with_dict(self, data, many, **kwargs):
        if type(data) is list:
            return {"data": data}
        else:
            return data

class SpecializationSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        ordered = True
        description = "This schema represents the attributes of the specialization"
    id = ma.Integer()
    name = ma.String(required=True, validate=[validate.Length(max=50)])
    image = ma.Url()
    
    @post_dump(pass_many=True)
    def wrap_with_dict(self, data, many, **kwargs):
        if type(data) is list:
            return {"data": data}
        else:
            return data
    
    @post_dump
    def transform_image_to_url(self, data, **kwargs):
        if data.get("image") is not None:
            data["image"] = generate_url(filename=data["image"])
        return data

class RoleSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Role
        ordered = True
        description = "This schema represents the attributes of the role"
    id = ma.auto_field(dump_only=True)
    role_name = ma.auto_field(required=True, validate=[validate.Length(max=20)], dump_only=True)

