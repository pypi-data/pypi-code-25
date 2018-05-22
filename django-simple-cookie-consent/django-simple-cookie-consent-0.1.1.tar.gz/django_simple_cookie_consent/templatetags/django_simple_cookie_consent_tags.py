from django import template
from django_simple_cookie_consent.models import CookieConsentSettings

register = template.Library()


@register.inclusion_tag('django_simple_cookie_consent/cookie_message.html')
def display_cookie_consent():
    cookie_settings = CookieConsentSettings.objects.first()
    if cookie_settings:
        return {
            'banner_colour': cookie_settings.banner_colour,
            'banner_text_colour': cookie_settings.banner_text_colour,
            'button_colour': cookie_settings.button_colour,
            'button_text_colour': cookie_settings.button_text_colour,
            'cookie_policy_link_text': cookie_settings.cookie_policy_link_text,
            'cookie_policy_link': cookie_settings.cookie_policy_link,
            'button_text': cookie_settings.button_text,
            'message': cookie_settings.message,
        }
    return {
        'no_cookie_settings': True
    }