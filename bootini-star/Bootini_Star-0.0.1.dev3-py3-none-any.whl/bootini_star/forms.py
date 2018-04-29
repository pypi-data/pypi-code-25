"""
Flask forms for logging in and signing up.
"""
__author__ = 'Ralph Seichter'

from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField, StringField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    email = StringField(
        u'E-Mail', validators=[DataRequired(message='We need your e-mail address.')])
    password = PasswordField(u'Password', validators=[
                             DataRequired(message='No password, no login.')])
    submit = SubmitField(u'Login')


class SignupForm(FlaskForm):
    email = StringField(
        u'E-Mail', validators=[DataRequired(message='We need your e-mail address.')])
    password = PasswordField(u'Password', validators=[
                             DataRequired(message='No password, no login.')])
    confirm = PasswordField(u'Confirm password', validators=[
                            DataRequired(message='Must match your password.')])
    submit = SubmitField(u'Sign me up')
