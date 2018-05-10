# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import multiplefilefield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('multiplefilefield_example', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MultipleMultipleFileFieldModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('hash', models.CharField(max_length=128)),
                ('files_1', multiplefilefield.fields.MultipleFileModelField(upload_to=b'')),
                ('files_2', multiplefilefield.fields.MultipleFileModelField(upload_to=b'')),
                ('files_3', multiplefilefield.fields.MultipleFileModelField(upload_to=b'')),
                ('files_4', multiplefilefield.fields.MultipleFileModelField(upload_to=b'')),
                ('files_5', multiplefilefield.fields.MultipleFileModelField(upload_to=b'')),
            ],
        ),
    ]
