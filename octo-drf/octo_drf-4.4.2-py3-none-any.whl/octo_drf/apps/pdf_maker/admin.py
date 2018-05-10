


from django import forms
from django.contrib import admin

from octo_drf.apps.base.admin import BaseAdmin
from octo_drf.apps.redactor.widgets import Redactor

from .models import PDFTemplate


class PDFTemplateAdminForm(forms.ModelForm):

    class Meta:
        widgets = {
            'content': Redactor,
        }


@admin.register(PDFTemplate)
class PDFTemplateAdmin(BaseAdmin):

    form = PDFTemplateAdminForm
    list_display = ('name', 'template')
    readonly_fields = ('template', )