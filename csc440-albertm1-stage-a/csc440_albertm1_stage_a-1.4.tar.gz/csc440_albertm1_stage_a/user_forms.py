from flask_wtf import Form
from wtforms import TextField
from wtforms.validators import InputRequired


class CreateUserForm(Form):
    """
    CreateUserForm can be used as a simple form to receive user input of a name and password.
    :param Form: flask_wtf Form instantiation.
    """
    name = TextField('', [InputRequired()])
    password = TextField('', [InputRequired()])


class DeleteUserForm(Form):
    """
        CreateUserForm can be used as a simple form to receive user input of a name and password.
        :param Form: flask_wtf Form instantiation.
    """
    id = TextField('', [InputRequired()])