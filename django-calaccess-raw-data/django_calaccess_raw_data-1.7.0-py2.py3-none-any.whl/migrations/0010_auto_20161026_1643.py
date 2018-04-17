# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-10-26 16:43
from __future__ import unicode_literals

import calaccess_raw.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('calaccess_raw', '0009_auto_20161026_1641'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cvr2campaigndisclosurecd',
            name='cmte_id',
            field=calaccess_raw.fields.CharField(blank=True, db_column='CMTE_ID', help_text='Committee identification number, when the entity is a committee', max_length=9),
        ),
    ]
