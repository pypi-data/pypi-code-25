# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('glitter_news', '0003_post_tags'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='date_url',
        ),
    ]
