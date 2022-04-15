from flask_wtf import FlaskForm
from wtforms import Form, BooleanField, StringField, PasswordField, validators

class SignUpForm(FlaskForm):
    username = StringField("Username", [
        validators.InputRequired(), 
        validators.Length(min=4, max=20, message="Username must be at least 4 characters long and max 20")
    ])

    firstName = StringField("First Name", [
        validators.InputRequired(),
        validators.Length(min=2, max=20),
    ])

    email = StringField("Email", [
        validators.InputRequired(), 
        validators.Email()
    ])

    password = PasswordField("Password", [
        validators.InputRequired(),
        validators.Regexp("^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?!.*\s).{8,24}$", 0,
            '''Password must contain at least one lowercase and one capital letter, a number and it must be 
            between 8 and 24 characters long'''),
        validators.EqualTo("confirmPassword", message="Passwords doesn't match")
    ])

    confirmPassword = PasswordField("Repeat Password", [
        validators.InputRequired(),
    ])

class LoginForm(FlaskForm):
    username = StringField("Username", [
        validators.InputRequired()
    ])
    password = PasswordField("Password", [
        validators.InputRequired(),
    ])

class changePasswordForm(FlaskForm):
    password = PasswordField("Current password", [
        validators.InputRequired(),
        validators.DataRequired()
    ])

    newPassword = PasswordField("New password", [
        validators.InputRequired(),
        validators.DataRequired(),
        validators.Regexp("^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?!.*\s).{8,24}$", 0,
            '''Password must contain at least one lowercase and one capital letter, a number and it must be 
            between 8 and 24 characters long'''),
        validators.EqualTo("confirmPassword", message="Passwords doesn't match")
    ])

    confirmPassword = PasswordField("Confirm password", [
        validators.InputRequired(),
        validators.DataRequired()
    ])