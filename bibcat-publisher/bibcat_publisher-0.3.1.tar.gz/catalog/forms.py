__author__ = "Jeremy Nelson"

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField

class LoginForm(FlaskForm):
    username = StringField("Account Name")
    password = PasswordField("Password")
