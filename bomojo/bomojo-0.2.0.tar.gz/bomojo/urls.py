"""
bomojo URL Configuration
"""

from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^movies/', include('bomojo.movies.urls')),
    url(r'^matchups/', include('bomojo.matchups.urls')),
]
