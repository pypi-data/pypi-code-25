from django.forms import Textarea
from django.conf import settings
from importlib import import_module


def html_widget():
    custom_widget = getattr(settings, 'HTML_FIELD_WIDGET', None)
    if not custom_widget:
        return Textarea
    if isinstance(custom_widget, str):
        return getattr(
            import_module(custom_widget.rsplit('.', 1)[0]),
            custom_widget.rsplit('.', 1)[1]
        )
    else:
        return custom_widget
