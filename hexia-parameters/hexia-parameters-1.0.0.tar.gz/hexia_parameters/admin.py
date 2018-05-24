from django.contrib import admin

# Register your models here.

from hexia_parameters.models import Parameter

class ParameterAdmin(admin.ModelAdmin):
    list_display = ['name', 'text']
    ordering = ['name',]
    readonly_fields = ['name']

    def get_actions(self, request):
        actions = super(ParameterAdmin, self).get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions
    
    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False
        
admin.site.register(Parameter, ParameterAdmin)