from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.core import mail

from lablackey.tests import ClientTestCase

class RegistrationTestCase(ClientTestCase):
  kwargs = {
    'username': 'somename',
    'email': 'email@example.com',
    'password': 'arstarst',
  }
  def test_urls(self):
    """ All these urls just return static pages."""
    urls = [
      (reverse("registration_complete"),'You cannot use this account until it is activated.')
    ]
    self.check_url(*urls[0])
  def test_activation(self):
    # register user
    response = self.client.post("/api/schema/lablackey.registration.RegistrationForm/",self.kwargs)
    user = get_user_model().objects.get(username=self.kwargs['username'])
    self.assertEquals(response.json()['ur_route_to'],reverse("registration_complete"))
    self.assertFalse(user.is_active)
    complete_url = reverse('registration_activate',args=[user.registrationprofile.activation_key])
    self.assertTrue(complete_url in mail.outbox[0].body)
    mail.outbox = []

    # activate user
    self.client.get(complete_url)
    user = get_user_model().objects.get(id=user.id)
    self.assertTrue(user.is_active)
    self.assertTrue(user.check_password(self.kwargs['password']))

    # attempting to reregister creates an error
    response = self.client.post("/api/schema/lablackey.registration.RegistrationForm/",self.kwargs)
    errors = response.json().get('errors',{})
    self.assertTrue(errors['username'] and errors['email'])
    mail.outbox = []

  def test_inactive_login(self):
    # register user and attempt to login
    response = self.client.post("/api/schema/lablackey.registration.RegistrationForm/",self.kwargs)
    mail.outbox = []
    response = self.client.post(reverse("login_ajax"),self.kwargs)
    messages = self.client.get("/").context['messages']._get()[0]
    self.assertTrue("Your account is inactive" in messages[0].message)
    self.check_subjects(["Activate your account"])
    
  def test_password_reset(self):
    pass
  def test_password_reset_activates(self):
    pass
