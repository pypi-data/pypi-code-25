from django.apps import apps
from django.conf import settings
from django.contrib.auth import authenticate, login, logout as _logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.validators import validate_email
from django.db.models import Q
from django import forms
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.template.response import TemplateResponse

from .forms import UserEmailForm, RequestModelForm, RequestForm
from loader import load_class
from .unrest import model_to_schema, form_to_schema, LazyEncoder

import json, random

def single_page_app(request,*args,**kwargs):
  """
  Load the base template and let the front end handle the rest.
  args and kwargs do nothing.
  """
  return TemplateResponse(request,'single_page_app.html',{'args':args,'kwargs':kwargs})

def render_template(request,*args,**kwargs):
  template = kwargs.get('template',"base.html")
  return TemplateResponse(request,template,kwargs)

redirect = lambda request,url: HttpResponseRedirect(url)

def login_ajax(request):
  if not ('username' in request.POST and 'password' in request.POST):
    return JsonResponse({ 'error': ['Please enter username and password'] })
  user = authenticate(username=request.POST['username'],password=request.POST['password'])
  if not user:
    return JsonResponse({ 'error': ['Username and password do not match.'] })
  login(request,user)
  view = getattr(settings,"USER_JSON_VIEW",None)
  if view:
    return load_class(view)(request)
  return JsonResponse({ 'user': {'id': user.id, 'username': user.username, 'email': user.email } })

def user_json(request):
  user = request.user
  if user.is_authenticated():
    keys = ['id','username','email','is_superuser','is_staff']
    return JsonResponse({ 'user': { k:getattr(user,k) for k in keys } })
  return JsonResponse({})

def logout(request):
  _logout(request)
  return HttpResponseRedirect("/")

def robots(request):
  if settings.DEBUG:
    return HttpResponse("User-agent: *\nDisallow: /")
  return HttpResponse("")

def register_ajax(request):
  User = get_user_model()
  email = request.POST.get('email',None)
  _Q = Q(email=email)|Q(username=email)
  for f in getattr(settings,"EXTRA_AUTH_FIELDS",[]):
    _Q = _Q | Q(**{f:email})
  matching_users = list(User.objects.filter(_Q))
  if email and 'password' in request.POST:
    user = authenticate(username=email,password=request.POST['password'])
    if user:
      login(request,user)
      return JsonResponse({'user': {'id': user.id, 'username': user.username, 'email': user.email } })
  if matching_users:
    return JsonResponse({"error": "A user with that email already exists. Please login or use another"},status=400)
  try:
    validate_email(email)
  except forms.ValidationError:
    return JsonResponse({"error": "Please enter a valid email address"},status=400)
  if not ('password' in request.POST and len(request.POST['password']) > 7):
    return JsonResponse({"error": "Please enter a password at least 8 characters long"},status=400)
  username = email.split("@")[0]
  while User.objects.filter(username=username):
    username = email.split("@")[0] + str(random.randint(0000,10000))
  user = User(
    email=email,
    username=username,
  )
  user.set_password(request.POST['password'])
  user.save()
  user.backend='django.contrib.auth.backends.ModelBackend'
  login(request,user)
  return JsonResponse({'user': {'id': user.id, 'username': user.username, 'email': user.email } })

@login_required
def set_email(request):
  form = UserEmailForm(request.POST or None,instance=request.user)
  if form.is_valid():
    form.save()
    messages.success(request,"Your email has been set, thank you.")
    return HttpResponseRedirect(request.POST.get("next","/"))
  values = {'form': form,'huh': 1}
  return TemplateResponse(request,"registration/set_email.html",values)

def get_schema(request,app_name,model_name):
  app = apps.get_app_config(app_name)
  model = app.get_model(model_name)
  return JsonResponse({'schema': model_to_schema(model) })

def get_form_schema(request,app_name,form_name,id=None):
  form = load_class("%s.forms.%s"%(app_name,form_name))
  if not form.user_is_allowed(request):
    raise NotImplementedError()
  args = [getattr(request,request.method) or None] # GET or POST
  kwargs = {'instance': getattr(form,'get_instance',lambda *a,**k: None)(request,id)} # for unrest like forms
  if issubclass(form,RequestModelForm):
    form = form(request,**kwargs)
  elif issubclass(form,RequestForm):
    kwargs.pop("instance")
    form = form(request,**kwargs)
  else:
    form = form(*args,**kwargs)

  if form.is_valid():
    form.save()
    return JsonResponse({
      'ur_route_to': getattr(form,"success_url",None) or request.POST.get("next",None),
      'messages': [{'level': 'success', 'body': "Form has been saved." }],
    })
  return JsonResponse(form_to_schema(form),encoder=LazyEncoder)
