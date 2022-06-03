from api import ma, token_auth
from marshmallow import validate, validates, validates_schema, ValidationError, post_load
from api.models import User

class UserSchema(ma.SQLAlchemyAutoSchema):
    """Schema defining the attributes of User"""
    class Meta:
        model = User
        ordered = True
        exclude = ("token", "token_expiration")
                
    id = ma.auto_field(dump_only=True)
    name = ma.auto_field(required=True, validate=[validate.Length(min=3, max=64)])
    email = ma.auto_field(required=True, validate=[validate.Length(max=120), validate.Email()])
    password = ma.auto_field(reqired=True, validate=validate.Length(min=8), load_only=True)
    registered_at = ma.auto_field(dump_only=True)
    confirmed = ma.auto_field(dump_only=True)
    dob = ma.auto_field(required=True)
    gender = ma.auto_field(required=True, validate=[validate.Length(max=8)])
    role_id = ma.auto_field(required=True)

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

