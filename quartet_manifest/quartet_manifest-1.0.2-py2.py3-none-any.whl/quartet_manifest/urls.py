# -*- coding: utf-8 -*-
from django.conf.urls import url

from . import views

app_name = 'quartet_manifest'

urlpatterns = [
    url(r'^quartet-manifest/$', views.get_apps, name='quartet-manifest'),
]
