from django.contrib.admin import ModelAdmin


class SuperUserDeletableAdminMixin(object):
    @staticmethod
    def has_delete_permission(request, obj=None):
        return request.user.is_superuser


class BaseModelAdmin(ModelAdmin):
    """Base admin class for BaseModel"""
    list_display = ('id', 'status', 'ordering', 'created')
    list_editable = ('status', 'ordering')
    list_filter = ('status',)
    ordering = ('ordering',)
    readonly_fields = ('created', 'updated')

    def get_fieldsets(self, request, obj=None):
        fieldsets = super(BaseModelAdmin, self).get_fieldsets(request, obj=obj)

        for field in ('created', 'updated'):
            if field not in fieldsets[0][1]['fields']:
                fieldsets[0][1]['fields'].append(field)

        return fieldsets
