from django.contrib import admin
from django.db import models

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

admin.site.register(AppCustomization)
