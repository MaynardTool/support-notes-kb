# file: app/admin/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length


class UserForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    display_name = StringField(
        "Display Name", validators=[DataRequired(), Length(min=2, max=100)]
    )
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6)])
    is_admin = BooleanField("Admin")
    is_active = BooleanField("Active")
    submit = SubmitField("Create User")


class ResetPasswordForm(FlaskForm):
    password = PasswordField("New Password", validators=[DataRequired(), Length(min=6)])
    submit = SubmitField("Reset Password")
