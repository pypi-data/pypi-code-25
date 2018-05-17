from django import forms
from django.contrib.auth import authenticate, password_validation
from django.utils.translation import gettext, gettext_lazy as _
from django.contrib.auth.forms import AuthenticationForm


# TODO: Not sure where to put this class view override for PleioLoginView
    # def done(self, form_list, **kwargs):
    #     self.request.session.set_expiry(30 * 24 * 60 * 60)


class LabelledLoginForm(AuthenticationForm):
        username = forms.CharField(required=True, max_length=254, widget=forms.TextInput(attrs={'id':"id_auth-username", 'aria-labelledby':"error_login"}))
        password = forms.CharField(required=True, strip=False, widget=forms.PasswordInput(attrs={'autocomplete':"off"}))

class ChangePasswordForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(ChangePasswordForm, self).__init__(*args, **kwargs)

    error_messages = {
        'invalid_password': _("The password is invalid."),
        'password_mismatch': _("The two password fields didn't match."),
    }

    old_password = forms.CharField(strip=False, widget=forms.PasswordInput(attrs={'aria-labelledby':"error_id_old_password"}))
    new_password1 = forms.CharField(strip=False, widget=forms.PasswordInput(attrs={'aria-labelledby':"error_id_new_password1"}))
    new_password2 = forms.CharField(strip=False, widget=forms.PasswordInput(attrs={'aria-labelledby':"error_id_new_password2"}))

    def clean_old_password(self):
        old_password = self.cleaned_data.get("old_password")
        user = authenticate(username=self.user.email, password=old_password)

        if user is None:
            raise forms.ValidationError(
                self.error_messages['invalid_password'],
                code='invalid_password',
            )

        return old_password

    def clean_new_password2(self):
        new_password1 = self.cleaned_data.get("new_password1")
        new_password2 = self.cleaned_data.get("new_password2")

        if new_password1 and new_password2 and new_password1 != new_password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )

        password_validation.validate_password(self.cleaned_data.get('new_password2'))
        return new_password2