# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import multiplefilefield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('multiplefilefield_example', '0002_multiplemultiplefilefieldmodel'),
    ]

    operations = [
        migrations.CreateModel(
            name='TestMultipleFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128)),
                ('files', multiplefilefield.fields.MultipleFileModelField(upload_to=b'')),
            ],
        ),
    ]
