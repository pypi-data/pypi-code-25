# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from random import random

from django.db import models
from django.contrib.postgres import fields as postgres_fields
from django.core.validators import RegexValidator

from slugify import slugify


class Matchup(models.Model):
    email = models.EmailField(blank=True, default='', db_index=True)
    title = models.CharField(blank=False, max_length=1024, db_index=True)
    slug = models.CharField(max_length=1024, db_index=True, unique=True)
    description = models.TextField(blank=True, default='')
    movies = postgres_fields.ArrayField(models.CharField(blank=False,
                                                         max_length=128))
    period = models.CharField(blank=True, default='', max_length=32,
                              validators=[RegexValidator(r'^\d+[dw]$')])
    featured = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            slug_base = slugify(self.title)
            self.slug = slug_base
            while Matchup.objects.filter(slug=self.slug).exists():
                self.slug = '%s-%s' % (slug_base, str(random())[2:])
        super(Matchup, self).save(*args, **kwargs)
