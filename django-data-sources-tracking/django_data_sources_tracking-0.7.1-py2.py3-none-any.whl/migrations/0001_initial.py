# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-01-09 13:36
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('url', models.CharField(max_length=255)),
                ('path', models.CharField(max_length=255)),
                ('type', models.SmallIntegerField(choices=[(0, 'tsv'), (1, 'csv'), (2, 'txt'), (3, 'vcf'), (4, 'bed'), (5, 'bigwig'), (6, 'wigfix'), (7, 'chromatograms'), (8, 'other')])),
                ('active', models.BooleanField(default=True)),
                ('relative_path', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name_plural': 'Files',
                'verbose_name': 'File',
            },
        ),
        migrations.AlterUniqueTogether(
            name='file',
            unique_together=set([('name', 'path'), ('name', 'url')]),
        ),
    ]
