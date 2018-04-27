# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('glitter_news', '0007_latestnewsblock_tags'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='is_sticky',
            field=models.BooleanField(default=False),
        ),
    ]
