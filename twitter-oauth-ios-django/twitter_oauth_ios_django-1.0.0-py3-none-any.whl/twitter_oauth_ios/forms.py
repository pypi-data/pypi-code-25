from datetime import datetime
from django import forms


class TwitterAuthForm(forms.Form):
    auth_time = forms.IntegerField(min_value=0, initial=int(datetime.now().strftime('%s')), required=True)
    user_id = forms.IntegerField(min_value=0, required=True)
    oauth_token = forms.CharField(required=True)
    oauth_token_secret = forms.CharField(required=True)
    screen_name = forms.CharField(required=True)
    display_name = forms.CharField(required=True)
