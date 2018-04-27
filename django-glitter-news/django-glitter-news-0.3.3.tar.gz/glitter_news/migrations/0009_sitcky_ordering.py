# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('glitter_news', '0008_post_is_sticky'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='post',
            options={'get_latest_by': 'date', 'default_permissions': ('add', 'change', 'delete', 'edit', 'publish'), 'ordering': ('-is_sticky', '-date')},
        ),
    ]
