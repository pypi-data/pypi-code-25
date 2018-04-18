# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-11-21 03:46
from __future__ import unicode_literals

from django.db import migrations, models
import djmoney.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('demo_models', '0009_auto_20151209_2136'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='birth_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='person',
            name='hammer_time',
            field=models.TimeField(blank=True, help_text="U Can't Touch This", null=True),
        ),
        migrations.AddField(
            model_name='person',
            name='last_login',
            field=models.DateField(auto_now=True),
        ),
        migrations.AddField(
            model_name='person',
            name='last_modifed',
            field=models.DateField(blank=True, null=True),
        ),
    ]
