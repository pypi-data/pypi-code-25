# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='RegistrationProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('activation_key', models.CharField(default=b'ACTIVATION_KEY', max_length=40, verbose_name='activation key')),
                ('expire_date', models.DateTimeField(null=True, blank=True)),
                ('activated', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ('-id',),
            },
            bases=(models.Model,),
        ),
    ]
