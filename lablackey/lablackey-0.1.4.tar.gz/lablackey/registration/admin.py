from django.contrib import admin, messages
from django.contrib.sites.requests import RequestSite
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _

from lablackey.registration.models import RegistrationProfile

class RawMixin(object):
  def formfield_for_dbfield(self, db_field, **kwargs):
    if db_field.name in self.raw_id_fields:
      kwargs.pop("request", None)
      type = db_field.rel.__class__.__name__
      if type == "ManyToOneRel":
        kwargs['widget'] = VerboseForeignKeyRawIdWidget(db_field.rel, site)
      elif type == "ManyToManyRel":
        kwargs['widget'] = VerboseManyToManyRawIdWidget(db_field.rel, site)
      return db_field.formfield(**kwargs)
    return super(RawMixin, self).formfield_for_dbfield(db_field, **kwargs)

class RegistrationAdmin(RawMixin,admin.ModelAdmin):
  actions = ['activate_users', 'resend_activation_email']
  list_display = ('user', 'expired')
  raw_id_fields = ['user']
  search_fields = ('user__username', 'user__first_name', 'user__last_name')

  def activate_users(self, request, queryset):
    for profile in queryset:
      RegistrationProfile.objects.activate_user(profile.activation_key)
  activate_users.short_description = _("Activate users")

  def resend_activation_email(self, request, queryset):
    if Site._meta.installed:
      site = Site.objects.get_current()
    else:
      site = RequestSite(request)

    for profile in queryset:
      profile.send_activation_email(site)
  resend_activation_email.short_description = _("Re-send activation emails")


admin.site.register(RegistrationProfile, RegistrationAdmin)
