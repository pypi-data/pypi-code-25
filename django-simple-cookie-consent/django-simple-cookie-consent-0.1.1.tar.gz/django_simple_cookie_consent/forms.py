from django import forms
from .models import CookieConsentSettings


class ColourWidget(forms.TextInput):
    input_type = 'color'


class CookieConsentSettingsForm(forms.ModelForm):
    class Meta:
        model = CookieConsentSettings
        fields = '__all__'
        widgets = {
            'banner_colour': ColourWidget(),
            'banner_text_colour': ColourWidget(),
            'button_colour': ColourWidget(),
            'button_text_colour': ColourWidget()
        }