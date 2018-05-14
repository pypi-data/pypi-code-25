"""URLs module"""
from django.conf import settings
from django.conf.urls import url

from optin import views

app_name = 'optin'

urlpatterns = [
    url(r'^amend-user-optins/(?P<pk>[\w\\-]+)/$', views.UpdateUserOptinView.as_view(), name='user_opt_selection'),
]
