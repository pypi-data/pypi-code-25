# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import

from django.conf.urls import url, include

from quartet_manifest.urls import urlpatterns as quartet_manifest_urls

app_name = 'quartet_manifest'

urlpatterns = [
    url(r'^', include(quartet_manifest_urls,
                      )),
]
