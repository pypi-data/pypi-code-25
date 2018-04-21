from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.sites.models import Site
from django.contrib.sites.requests import RequestSite
from django.http import JsonResponse, HttpResponseRedirect
from django.utils import timezone

from lablackey.mail import send_template_email

try:
  from lablackey.registration.models import RegistrationProfile
except RuntimeError:
  pass

import urllib2, datetime

def resend_activation(target):
  def wrapper(request,*args,**kwargs):
    data = request.POST or request.GET
    model = get_user_model()
    if data.get('username',None):
      try:
        if hasattr(model.objects,"keyword_search"):
          user = model.objects.keyword_search(data.get('username'),force_active=False)[0]
        else:
          user = model.objects.get(username=data.get("username"))
        if not user.is_active and user.check_password(data.get("password","")[:200]):
          messages.error(request,"Your account is inactive. Please check your email (%s) for an activation link. If you no longer have access to this email address, please contact %s"%(user.email,settings.MEMBERSHIP_EMAIL))
          if Site._meta.installed:
            site = Site.objects.get_current()
          else:
            site = RequestSite(request)
          profile,new = RegistrationProfile.objects.get_or_create(user=user)
          profile.expire_date = timezone.now() + datetime.timedelta(days=settings.ACCOUNT_ACTIVATION_DAYS)
          profile.save()
          profile.send_activation_email(site)
          return JsonResponse({'ur_route_to': "" })
      except (model.DoesNotExist,IndexError):
        pass
    return target(request,*args,**kwargs)
  return wrapper

def auth_required(func, **decorator_kwargs):
  # kwargs can be redirect_field_name and login_url (see login_required)
  def wrapper(request, *args, **kwargs):
    user=request.user  
    if request.user.is_authenticated():
      return func(request, *args, **kwargs)
    if request.is_ajax():
      response = JsonResponse({'status': 401,'error': "You must be logged in to continue"},status=400)
      #response['WWW-Authenticate'] = 'Basic realm="api"'
      return response
    return login_required(func)(request,**decorator_kwargs)
  wrapper.__doc__ = func.__doc__
  wrapper.__name__ = func.__name__
  return wrapper

def email_required(func):
  def wrap(request, *args, **kwargs):
    if not request.user.is_authenticated():
      return auth_required(func)(request,**kwargs)
    if not request.user.email:
      return HttpResponseRedirect("/set_email/?next=%s"%urllib2.quote(request.path))
    return func(request, *args, **kwargs)
  wrap.__doc__=func.__doc__
  wrap.__name__=func.__name__
  return wrap

def cached_method(target,name=None):
  target.__name__ = name or target.__name__
  if target.__name__ == "<lambda>":
    raise ValueError("Using lambda functions in cached_methods causes __name__ collisions.")
  def wrapper(*args, **kwargs):
    obj = args[0]
    name = '___' + target.__name__

    if not hasattr(obj, name):
      value = target(*args, **kwargs)
      setattr(obj, name, value)
        
    return getattr(obj, name)
      
  return wrapper

def cached_property(target,name=None):
  return property(cached_method(target,name=name))

def activate_user(target):
  def wrapper(request,*args,**kwargs):
    data = request.POST or request.GET
    model = get_user_model()
    if data.get('email',None):
      try:
        if hasattr(model.objects,"keyword_search"):
          user = model.objects.keyword_search(data.get('email'))[0]
        else:
          user = model.objects.get(email=data.get("email"))
        user.is_active = True
        user.save()
      except (model.DoesNotExist,IndexError):
        send_template_email("email/no_user",[data.get("email")],context={})
    return target(request,*args,**kwargs)
  return wrapper

def timebomb(check_function=lambda request,*args,**kwargs: False):
  """
  A wrapper to quickly tell if a API request is out of date or not.
  check_function should look at request.GET['__when'] and tell if the data is newer than that time.
  if False: data is expired. return the new data with a timestamp.
  if True: return "okay" and a timestamp of when was checked (in server timezone).
  check_function should be optimized to be as faster than the view function (otherwise what's the point?)
  Note that views using timebomb should return a json.dumps-able dict, not an HttpResponse.
  wrap with @timebomb() to always declare data stale.
  """
  def decorator(target):
    def wrapper(request,*args,**kwargs):
      if check_function(request,*args,**kwargs):
        return JsonResponse({'__timebomb': 'okay','__when': timezone.now()})
      data = target(request,*args,**kwargs)
      data['__when'] = timezone.now()
      return JsonResponse(data)
    return wrapper
  return decorator
