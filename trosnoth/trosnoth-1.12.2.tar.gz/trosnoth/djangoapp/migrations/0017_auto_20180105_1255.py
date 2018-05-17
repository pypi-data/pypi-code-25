# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trosnoth', '0016_auto_20171222_1548'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trosnotharena',
            name='autoStartCountDown',
            field=models.IntegerField(default=90, verbose_name=b'Automatically start new game after (seconds, negative to disable)'),
        ),
    ]
