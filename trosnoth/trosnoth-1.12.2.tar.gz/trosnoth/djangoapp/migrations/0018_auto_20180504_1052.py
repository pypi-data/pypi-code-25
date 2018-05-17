# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trosnoth', '0017_auto_20180105_1255'),
    ]

    operations = [
        migrations.AddField(
            model_name='gameplayer',
            name='boardScore',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='gamerecord',
            name='blueTeamScore',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='gamerecord',
            name='playerScoresEnabled',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='gamerecord',
            name='redTeamScore',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='gamerecord',
            name='scenario',
            field=models.TextField(default=b''),
        ),
        migrations.AddField(
            model_name='gamerecord',
            name='teamScoresEnabled',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='gameplayer',
            name='user',
            field=models.ForeignKey(blank=True, to='trosnoth.TrosnothUser', null=True),
        ),
        migrations.AlterField(
            model_name='playerkills',
            name='killer',
            field=models.ForeignKey(related_name='+', blank=True, to='trosnoth.GamePlayer', null=True),
        ),
    ]
