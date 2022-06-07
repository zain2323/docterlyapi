from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.fields import BooleanField
from wtforms.validators import DataRequired, EqualTo, Length, Email, ValidationError
from wtforms.fields.simple import PasswordField, SubmitField
from api.models import User

# Validator that checks every field is free from slash (/) because this may cause error in some cases.
def check_slash(form, field):
    if "/" in field.data:
        raise ValidationError("\ is not allowed.")

class SignUpForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(message="Name field can not be empty!"),
                                          Length(min=3, max=30), check_slash])
    email = StringField('Email', validators=[DataRequired(message="Email field can not be empty!"),
                                            Length(min=5, max=30), Email(), check_slash])
    password = PasswordField("Password", validators=[DataRequired(message="Password field can not be empty!"),
                                            Length(min=8, max=60, message="Password length should be atleast 8 characters!"), check_slash])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(message="Confirm password field can not be empty!"),
                                            EqualTo('password', message="Password mismatch"), check_slash])
    submit = SubmitField("Sign Up")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("This email is already taken!")

class SignInForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(message="Email field can not be empty!"),
                                            Length(min=5, max=30), Email(), check_slash])
    password = PasswordField("Password", validators=[DataRequired(message="Password field can not be empty!"),
                                            Length(min=8, max=60, message="Password length should be atleast 8"), check_slash])
    remember_me = BooleanField("Remember me")
    submit = SubmitField("Login")