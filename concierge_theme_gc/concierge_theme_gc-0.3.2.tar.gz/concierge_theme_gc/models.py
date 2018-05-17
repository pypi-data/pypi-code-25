from django.contrib import admin
from django.db import models
from django.contrib.auth.admin import UserAdmin
from django.contrib.admin import ModelAdmin

from core.models import User

# TODO: GC difference: receives_newsletter defaults to True

class AppCustomization(models.Model):
    BG_IMAGE_OPTIONS = (
        ('C', 'Cover'),
        ('T', 'Tiled'),
    )

    product_title = models.CharField(max_length=50)
    color_hex = models.CharField("your product's main brand color (Hex)", max_length=6)
    logo_image = models.ImageField(null=True, blank=True)
    app_favicon = models.ImageField(null=True, blank=True)
    app_background_photo = models.ImageField(null=True, blank=True)
    app_background_options = models.CharField(max_length=1, choices=BG_IMAGE_OPTIONS)
    custom_helpdesk_link = models.CharField(max_length=100, default='', blank=True)
    display_language_toggle = models.BooleanField(default=True)
    email_language_toggle = models.BooleanField("Display all system languages in emails", default=True)
    display_logo_title = models.BooleanField("Display Logo and Title together", default=True)
    footer_image_left = models.FileField(null=True, blank=True)
    footer_image_right = models.FileField(null=True, blank=True)

class UserAdmin(UserAdmin):
    search_fields = ModelAdmin.search_fields = ('username', 'name', 'email',)
    list_filter = ModelAdmin.list_filter + ('is_active', 'is_admin',)
    list_display = ModelAdmin.list_display + ('is_active',)
    filter_horizontal = ()
    ordering = ('-id', )
    fieldsets = add_fieldsets = (
        (None, {'fields': ('last_login', 'name', 'email', 'password', 'avatar',)}),
        ('Settings', {'fields': ('accepted_terms', 'receives_newsletter', 'is_active', 'is_admin',)}),
    )


admin.site.register(AppCustomization)
# admin.site.register(User, UserAdmin)   -- can't register it twice...
