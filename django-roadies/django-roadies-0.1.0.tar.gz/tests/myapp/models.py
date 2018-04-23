from __future__ import absolute_import, print_function, unicode_literals

from django.db import models


class Foo(models.Model):

    bar = models.CharField(max_length=16)

    def __str__(self):
        return self.bar


def test_handler(sender, **kwargs):
    pass
