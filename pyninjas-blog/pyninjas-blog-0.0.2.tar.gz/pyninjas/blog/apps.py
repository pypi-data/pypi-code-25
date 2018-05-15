from django.utils.translation import ugettext_lazy as _
from django.apps import AppConfig


class BlogConfig(AppConfig):
    name = 'pyninjas.blog'
    verbose_name = _("Blog")
