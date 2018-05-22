from django.contrib import admin
from .forms import CookieConsentSettingsForm
from .models import CookieConsentSettings


class CookieConsentSettingsAdmin(admin.ModelAdmin):
    form = CookieConsentSettingsForm

    def has_add_permission(self, request):
        return False if self.model.objects.count() > 0 else super(CookieConsentSettingsAdmin, self).has_add_permission(request)
admin.site.register(CookieConsentSettings, CookieConsentSettingsAdmin)