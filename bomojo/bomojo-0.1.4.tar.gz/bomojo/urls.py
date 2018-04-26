"""
bomojo URL Configuration
"""

from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^movies/', include('movies.urls')),
    url(r'^matchups/', include('matchups.urls')),
]
