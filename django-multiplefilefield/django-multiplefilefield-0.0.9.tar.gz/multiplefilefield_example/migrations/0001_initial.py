# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import multiplefilefield.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SimpleMultipleFileFieldModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('hash', models.CharField(max_length=128)),
                ('files', multiplefilefield.fields.MultipleFileModelField(upload_to=b'')),
            ],
        ),
    ]
