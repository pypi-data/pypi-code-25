from django import forms
from django.forms import ModelForm

from .fields import RemoteImageField

class ExampleForm(forms.Form):
    remote_image = RemoteImageField(required=True)
    
class ExampleWhitelistedPNGForm(forms.Form):
    remote_image = RemoteImageField(required=True, ext_whitelist=['png'])

class ExampleBlacklistedPNGForm(forms.Form):
    remote_image = RemoteImageField(required=True, ext_blacklist=['png'])
