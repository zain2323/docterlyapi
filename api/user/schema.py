from api import ma, token_auth
from marshmallow import validate, validates, validates_schema, ValidationError, post_load, fields
from api.models import User, Role
from api.webadmin.schema import RoleSchema

class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        ordered = True
        description = "This schema represents the attributes of the user"
    id = ma.Integer()
    name = ma.String(required=True, validate=[validate.Length(min=3, max=64)])
    email = ma.Email(required=True, validate=[validate.Length(max=120), validate.Email()])
    password = ma.String(reqired=True, validate=validate.Length(min=8), load_only=True)
    registered_at = ma.DateTime()
    confirmed = ma.Boolean()
    role = ma.String(required=True)
    # dob = ma.Date(required=True)
    # gender = ma.String(required=True, validate=[validate.Length(max=8)])

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
        data["role"] = Role.query.filter_by(role_name=data['role']).first()
        return data
    
    # @validates("gender")
    # def validate_gender(self, value):
    #     value = value.lower()
    #     if value not in ["male", "female"]:
    #         raise ValidationError("Invalid gender")

