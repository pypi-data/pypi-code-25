from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse

from .forms import RegistrationForm
from .models import RegistrationProfile

def register(request,form=RegistrationForm):
    form = form(request)
    if form.is_valid():
        form.save()
        return HttpResponseRedirect(reverse('registration_complete'))
    values = { 'form': form }
    return TemplateResponse(request,'registration/registration_form.html',values)

def activate(request,activation_key):
    profile, activated = RegistrationProfile.objects.get_and_activate(activation_key)
    if activated: # success! login
        user = profile.user
        user.backend='django.contrib.auth.backends.ModelBackend'
        login(request,user)
        m = "Welcome %s. Your account has been activated and you have been logged in."%user
        messages.success(request,m)
        return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
    values = {
        'profile': profile,
    }
    return TemplateResponse(request,'registration/activate.html',values)
