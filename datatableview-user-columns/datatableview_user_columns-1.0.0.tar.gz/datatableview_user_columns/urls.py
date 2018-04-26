# -*- coding: utf-8 -*-
"""urls.py: Django """

from __future__ import unicode_literals
from __future__ import print_function

import logging

from django.conf.urls import url

from .views import DataTableUserColumnsListView, DataTableUserColumnsUpdateView, DataTableUserColumnsCreateView, \
    DataTableUserColumnsDeleteView

__author__ = 'Steven Klass'
__date__ = '8/10/17 11:41'
__copyright__ = 'Copyright 2017 IC Manage. All rights reserved.'
__credits__ = ['Steven Klass', ]

log = logging.getLogger(__name__)

urlpatterns = [
    url(r'^user_columns/$', DataTableUserColumnsListView.as_view(), name="user_table_list"),
    url(r'^user_columns/create/(?P<table_name>[A-Za-z0-9_\.]+)/$', DataTableUserColumnsCreateView.as_view(), name="user_table_create"),
    url(r'^user_columns/update/(?P<pk>\d+)/$', DataTableUserColumnsUpdateView.as_view(), name="user_table_update"),
    url(r'^user_columns/delete/(?P<pk>\d+)/$', DataTableUserColumnsDeleteView.as_view(), name="user_table_delete"),
]
