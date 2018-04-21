from django.apps import apps
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.core import mail
from django.core.management import call_command
from django.core.urlresolvers import reverse
from django.test import TestCase, Client

import random, os

def _check(a,b):
  success = sorted(a) == sorted(b)
  if not success:
    raise ValueError("\ndesired: %s \nactual  : %s"%(sorted(a),sorted(b)))
  return success

def check_subjects(subjects,outbox=None):
  print "DEPRACATED! Use ClientTestCase.check_subjects instead!"
  if not outbox:
    outbox = mail.outbox
  outbox_subjects = [m.subject.replace(settings.EMAIL_SUBJECT_PREFIX,'') for m in outbox]
  return _check(subjects,outbox_subjects)

def check_recipients(recipients,outbox=None):
  print "DEPRACATED! Use ClientTestCase.check_recipients instead!"
  if not outbox:
    outbox = mail.outbox
  outbox_recipients = [m.recipients() for m in outbox]
  return _check(recipients,outbox_recipients)

class ClientTestCase(TestCase):
  """
  A TestCase with added functionality such as user/object creationg, login/logout.
  """
  _passwords = {}
  fixture_apps = []
  verbosity = 0
  def setUp(self):
    Site.objects.create(domain='testserver')
    for app_name in self.fixture_apps:
      app = apps.get_app_config(app_name)
      self.call_command("loaddata",os.path.join(app.module.__path__[0],"fixtures/test.json"))
  def call_command(self,*args):
    """ A wrapper around django.core.management.commands.call_command which sets "-v self.verbosity" """
    args = list(args)
    args.append("-v %s"%self.verbosity)
    call_command(*args)
  def check_url(self,url,snippet):
    response = self.client.get(url)
    self.assertTrue(snippet in str(response.render()))
  def login(self,username,password=None):
    if isinstance(username,get_user_model()):
      username = username.username
    user = get_user_model().objects.get(username=username)
    _pw = self._passwords.get(username,"nope")
    if not user.check_password(password or _pw):
      user.set_password(password)
      user.save()
    self.client.post(reverse('login'),{'username': username,'password': password or _pw})
    return user
  def logout(self):
    self.client.get(reverse('logout'))
  def _new_object(self,model,**kwargs):
    return model.objects.create(**kwargs)
  def new_user(self,username=None,password=None,**kwargs):
    user = self._new_object(get_user_model(),username=username or "user_%s"%random.random(),**kwargs)
    self._passwords[user.username] = password = password or "%s"%random.random()
    user.email = user.username + ("" if "@" in user.username else "@example.com")
    user.set_password(password)
    user.save()
    return user
  def check_subjects(self,subjects,outbox=None):
    outbox = outbox or mail.outbox
    out_subjects = [m.subject.replace(settings.EMAIL_SUBJECT_PREFIX,'') for m in outbox]
    self.assertTrue(_check(subjects,out_subjects))
  def check_recipients(self,recipients,outbox=None):
    outbox = outbox or mail.outbox
    self.assertTrue(_check(recipients,[m.recipients() for m in outbox]))
