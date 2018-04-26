# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='DataTableUserColumns',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('table_name', models.CharField(max_length=128)),
                ('columns', models.TextField()),
                ('last_updated', models.DateTimeField(default=django.utils.timezone.now)),
                ('user', models.ForeignKey(related_name='datatable_colums', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'permissions': (('view_datatableusercolumns', 'View Datatable User Columns'),),
            },
        ),
    ]
