from django.contrib import admin

# Register your models here.
from django.contrib.postgres import fields
from django_json_widget.widgets import JSONEditorWidget

from django_orion_model.models import Scope, Broker, OrionEntity


@admin.register(OrionEntity)
class OrionEntityAdmin(admin.ModelAdmin):
    formfield_overrides = {
        fields.JSONField: {'widget': JSONEditorWidget},
    }


@admin.register(Broker)
class BrokerAdmin(admin.ModelAdmin):
    pass


@admin.register(Scope)
class ScopeAdmin(admin.ModelAdmin):
    pass
