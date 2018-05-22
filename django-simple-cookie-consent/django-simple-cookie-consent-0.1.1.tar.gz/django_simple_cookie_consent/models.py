from django.db import models


class CookieConsentSettings(models.Model):
    message = models.TextField(
        default="This website uses cookies to ensure you get the best experience on our website."
    )

    button_text = models.CharField(
        default="Got it!",
        max_length=255
    )

    cookie_policy_link = models.CharField(
        max_length=255
    )

    cookie_policy_link_text = models.CharField(
        default="Learn more",
        max_length=255
    )

    banner_colour = models.CharField(
        default="#252e39",
        max_length=255
    )

    banner_text_colour = models.CharField(
        default="#ffffff",
        max_length=255
    )

    button_colour = models.CharField(
        default="#3acdf6",
        max_length=255
    )

    button_text_colour = models.CharField(
        default="#ffffff",
        max_length=255
    )
