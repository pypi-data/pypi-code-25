from django.contrib import admin
from django.forms import Textarea
from django.db import models
from deeppages.models import Page


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {
            'widget': Textarea(attrs={'rows': 20, 'style': 'width: 99%;'})
        },
    }
