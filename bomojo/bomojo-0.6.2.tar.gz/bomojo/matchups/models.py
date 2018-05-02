# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from random import random

from django.conf import settings
from django.contrib.postgres import fields as postgres_fields
from django.core.validators import RegexValidator
from django.db import models

from slugify import slugify


class Matchup(models.Model):
    class Meta:
        db_table = 'matchups_matchup'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='matchups')
    title = models.CharField(blank=False, max_length=1024, db_index=True)
    slug = models.CharField(max_length=1024, db_index=True, unique=True)
    description = models.TextField(blank=True, default='')
    movies = postgres_fields.ArrayField(models.CharField(blank=False,
                                                         max_length=128))
    period = models.CharField(blank=True, default='', max_length=32,
                              validators=[RegexValidator(r'^\d+[dw]$')])
    featured = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            slug_base = slugify(self.title)
            self.slug = slug_base
            while Matchup.objects.filter(slug=self.slug).exists():
                self.slug = '%s-%s' % (slug_base, str(random())[2:])
        super(Matchup, self).save(*args, **kwargs)
