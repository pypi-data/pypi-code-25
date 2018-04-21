from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib.auth import get_user_model
from django.views.generic.base import TemplateView
from django.utils import timezone

import views, auth_urls, datetime
from lablackey.decorators import resend_activation
import lablackey.views

urlpatterns = [
  url(r'^register/$',lablackey.views.single_page_app,name="register"),
  url(r'^register/complete/$',lablackey.views.render_template,kwargs={"template":"registration/complete.html"},
      name='registration_complete'),
  url(r'^register/(\w+)/$',views.activate,name='registration_activate'),
  url(r'^activate/(\w+)/$',views.activate), #! DEPRACATED in favor of the above
]
