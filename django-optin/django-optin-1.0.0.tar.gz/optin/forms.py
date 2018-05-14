from django.forms import ModelForm, modelformset_factory
from django import forms

from optin.models import UserOptin
from optin.utils import USER_MODEL

class UserForm(forms. ModelForm):
    class Meta:
        model = USER_MODEL
        fields = ['id']
        widgets = {
            'id' : forms.HiddenInput()
        }


class UserOptinForm(ModelForm):
    class Meta:
        model = UserOptin
        exclude = ['id']
        widgets = {
            'option' : forms.RadioSelect(),
            'user' : forms.HiddenInput(),
            'category' : forms.HiddenInput()
        }
    

UserOptinFormSet = forms.modelformset_factory(
    UserOptin, 
    fields= '__all__', 
    extra=0,
    widgets = {
            'user' : forms.HiddenInput(),
            'category' : forms.HiddenInput(),
            'id' : forms.HiddenInput()
        }
    )