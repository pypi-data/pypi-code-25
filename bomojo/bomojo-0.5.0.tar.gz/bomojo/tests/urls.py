"""
bomojo test URL Configuration

This module only exists to add a login view for the tests, since some of the
views in the API require authentication.
"""

from django.conf.urls import include, url

from bomojo.tests.views import login

urlpatterns = [
    url(r'^', include('bomojo.urls')),
    url(r'^login/', login),
]
