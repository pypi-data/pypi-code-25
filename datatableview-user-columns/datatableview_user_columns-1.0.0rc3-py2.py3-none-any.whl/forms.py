# -*- coding: utf-8 -*-
"""forms.py: Django datatable_user_columns"""

from __future__ import unicode_literals
from __future__ import print_function

import logging

from django import forms
from django.core import validators

from datatableview_user_columns.models import DataTableUserColumns

__author__ = 'Steven Klass'
__date__ = '8/17/17 08:43'
__copyright__ = 'Copyright 2017 IC Manage. All rights reserved.'
__credits__ = ['Steven Klass', ]

log = logging.getLogger(__name__)


class UserColumnsUpdateForm(forms.ModelForm):
    """Update User Columns"""
    columns = forms.MultipleChoiceField(required=True, label="Columns")

    def __init__(self, choices, *args, **kwargs):
        super(UserColumnsUpdateForm, self).__init__(*args, **kwargs)
        self.fields['columns'].choices = choices

    def clean_columns(self):
        columns = self.cleaned_data['columns']
        if isinstance(columns, basestring):
            columns = columns.strip()
        return ",".join(columns)

    class Meta(object):
        model = DataTableUserColumns
        fields = ('columns',)