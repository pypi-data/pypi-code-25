from __future__ import absolute_import, print_function, unicode_literals

from django.db.models.signals import post_save
from .models import test_handler

post_save.connect(test_handler, dispatch_uid='test_handler')
