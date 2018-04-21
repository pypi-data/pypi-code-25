from django.apps import apps
from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.test import RequestFactory

request_factory = RequestFactory()
from .serializers import BaseSizzler
from lablackey.api import views

def import_serializers(app):
  app_name = app.name
  try:
    app_serializers = __import__(app_name+".serializers",fromlist=['serializers'])
  except ImportError:
    return []

  #! TODO
  #really this next line should be isinstance of a custom class
  #autosizzler should also be of that class
  return [(name, cls) for name, cls in app_serializers.__dict__.items() if name.endswith("Sizzler")]

#! TODO This is currently not used, it was an attempt to make the admin auto work with this.
def auto_serializer(model, modeladmin):
  request = request_factory.get('/')
  request.user = get_user_model()(is_superuser=True)

  class AutoSizzler(BaseSizzler):
    class Meta:
      pass
  AutoSizzler.Meta.model = model
  fields = list(modeladmin.get_fields(request))
  #if not model._meta.pk.name in fields:
  #  fields.append(model._meta.pk.name)
  #AutoSizzler.Meta.fields = fields
  return AutoSizzler

def build_urls():
  #! TODO This should be split into build_map and build_urls
  #! TODO look into how admin register goes and do it here too.
  app_map = {}
  out = []
  for app in apps.get_app_configs():
    app_map[app] = {}
    for name,serializer in import_serializers(app):
      url_name = name.lower()
      if url_name.endswith("sizzler"):
        url_name = url_name[:-7] # len("sizzler")
      app_map[app][url_name] = serializer
  for app, d in app_map.items():
    for s_name, serializer in d.items():
      kwargs = {'serializer': serializer}
      _url = u'^api/(%s)/(%s)/'%(app.label,s_name)
      out.append(url(_url+"$",views.list_view,name="api_list_view",kwargs=kwargs))
      out.append(url(_url+"(\d+)/$",views.detail_view,name="api_detail_view",kwargs=kwargs))
  return out
