# -*- coding: utf-8 -*-
"""views.py: Django """

from __future__ import unicode_literals
from __future__ import print_function

import importlib
import logging
import os
import inspect

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse

import datatables
from datatableview_user_columns.forms import UserColumnsUpdateForm
from .models import DataTableUserColumns
from django.views.generic import CreateView, DeleteView

__author__ = 'Steven Klass'
__date__ = '8/10/17 11:41'
__copyright__ = 'Copyright 2017 IC Manage. All rights reserved.'
__credits__ = ['Steven Klass', ]

log = logging.getLogger(__name__)

try:
    from apps.core.views.generics import AuthenticationMixin
except:
    log.warning("No auth mixin found!")
    class AuthenticationMixin(object):
        pass

try:
    from apps.core.views.generics import IPCUpdateView as UpdateView
except:
    from django.views.generic import UpdateView


try:
    from apps.core.views.generics import IPCDatatableView as DatatableMixin
except:
    log.warning("No IPC Datatable view found!")
    from datatables.views import DatatableMixin


class DataTableUserMixin(DatatableMixin):

    def get_datatable_kwargs(self, **kwargs):
        kwargs = super(DataTableUserMixin, self).get_datatable_kwargs(**kwargs)
        kwargs['user'] = self.request.user
        kwargs['table_name'] = self.get_table()
        return kwargs

    def get_table(self):
        filename = inspect.getfile(self.__class__)
        package = os.path.basename(os.path.dirname(filename))
        module = os.path.splitext(os.path.basename(filename))[0]
        return ".".join([package, module, self.__class__.__name__])


class DataTableUserColumnsCreateView(AuthenticationMixin, CreateView):

    def get(self, request, *args, **kwargs):

        _import = ".".join(kwargs.get('table_name').split(".")[:-1])
        _class = kwargs.get('table_name').split(".")[-1]

        i = importlib.import_module(_import, [_class])
        datatable_class = getattr(i, _class).datatable_class

        obj, create = DataTableUserColumns.objects.get_or_create(
            user=request.user, table_name=kwargs.get('table_name'),
            defaults={'columns': ",".join(datatable_class.default_columns)})

        next_page = self.request.GET.get('next', "")
        if len(next_page):
            next_page = "?next=" + next_page

        return HttpResponseRedirect(reverse('user_table_update', kwargs=dict(pk=obj.id)) + next_page)


class DataTableUserColumnsUpdateView(UpdateView):
    form_class = UserColumnsUpdateForm

    def get_queryset(self):
        return DataTableUserColumns.objects.all()

    def get_form_kwargs(self):
        kwargs = super(DataTableUserColumnsUpdateView, self).get_form_kwargs()
        kwargs['choices'] = self.object.get_available_column_choices()
        kwargs['initial'] = {'columns': self.object.columns.split(",")}
        return kwargs

    def get_cancel_url(self):
        return self.request.GET.get('next', "/")

    def get_success_url(self):
        return self.request.GET.get('next', "/")

    def get_context_data(self, **kwargs):
        data = super(DataTableUserColumnsUpdateView, self).get_context_data(**kwargs)
        data['next'] = self.request.GET.get('next')
        data['column_choices'] = [x[1] for x in self.object.get_available_column_choices()]
        data['delete_url'] = reverse('user_table_delete', kwargs=dict(pk=self.object.id))
        return data

class DataTableUserColumnsDeleteView(DeleteView):

    def get_queryset(self):
        return DataTableUserColumns.objects.all()

    def get_success_url(self):
        return self.request.GET.get('next', "/")

    def get(self, *args, **kwargs):
        return self.post(*args, **kwargs)
#
# Example using our own system...
#


class DataTableUserColumnsListView(DataTableUserMixin):
    permission_required = 'ip_verification.view_regressiontagsummary'
    datatable_class = datatables.DataTableUserColumnsDataTable
    show_add_button = False

    def get_queryset(self):
        return DataTableUserColumns.objects.all()

