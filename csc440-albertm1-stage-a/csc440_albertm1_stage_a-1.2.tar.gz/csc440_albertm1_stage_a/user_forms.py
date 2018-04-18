from flask_wtf import Form
from wtforms import TextField
from wtforms.validators import InputRequired


class CreateUserForm(Form):
    name = TextField('', [InputRequired()])
    password = TextField('', [InputRequired()])


class DeleteUserForm(Form):
    id = TextField('', [InputRequired()])