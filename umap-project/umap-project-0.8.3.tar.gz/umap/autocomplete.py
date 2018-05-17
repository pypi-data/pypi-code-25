from agnocomplete.register import register
from agnocomplete.core import AgnocompleteModel
from django.contrib.auth import get_user_model


@register
class AutocompleteUser(AgnocompleteModel):
    model = get_user_model()
    fields = ['username']
