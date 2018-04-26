# -*- coding: utf-8 -*-
"""models.py: Django """

from __future__ import unicode_literals
from __future__ import print_function

import importlib
import logging

from django.conf import settings
from django.db import models
from django.utils.timezone import now

__author__ = 'Steven Klass'
__date__ = '8/10/17 11:41'
__copyright__ = 'Copyright 2017 IC Manage. All rights reserved.'
__credits__ = ['Steven Klass', ]

log = logging.getLogger(__name__)


class DataTableUserColumns(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='datatable_colums')
    table_name = models.CharField(max_length=128)
    columns = models.TextField()

    last_updated = models.DateTimeField(default=now)

    class Meta:
        permissions = (('view_datatableusercolumns', "View Datatable User Columns"),)
        verbose_name = "Datatable user defined columns"
        verbose_name_plural = "Datatable user defined columns's"

    def __unicode__(self):
        return self.table_name.split(".")[-1]

    def save(self, *args, **kwargs):
        self.last_updated = now()
        return super(DataTableUserColumns, self).save(*args, **kwargs)

    def get_datatable_class(self):
        _import = ".".join(self.table_name.split(".")[:-1])
        _class = self.table_name.split(".")[-1]

        i = importlib.import_module(_import, [_class])
        return getattr(i, _class).datatable_class

    def get_available_column_choices(self):
        datatable_class = self.get_datatable_class()
        return[(k, v.label)for k, v in datatable_class.base_columns.items()]

