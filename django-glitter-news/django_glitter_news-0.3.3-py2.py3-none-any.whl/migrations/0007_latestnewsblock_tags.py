# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('glitter_news', '0006_populate_category_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='latestnewsblock',
            name='tags',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
