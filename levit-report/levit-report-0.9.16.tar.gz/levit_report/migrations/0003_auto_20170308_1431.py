# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-03-08 14:31
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('levit_report', '0002_auto_20170114_0758'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='get_language_from_target',
            field=models.BooleanField(default=False, verbose_name='get language from target'),
        ),
        migrations.AlterField(
            model_name='document',
            name='content_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reports', to='contenttypes.ContentType', verbose_name='content type'),
        ),
        migrations.AlterField(
            model_name='document',
            name='convert_to',
            field=models.CharField(blank=True, choices=[('pdf', 'pdf'), ('doc', 'doc'), ('docx', 'docx'), ('xls', 'xls'), ('xlsx', 'xlsx')], max_length=5, null=True, verbose_name='convert to'),
        ),
        migrations.AlterField(
            model_name='document',
            name='merge_with_tos',
            field=models.BooleanField(default=False, verbose_name='merge with tos'),
        ),
        migrations.AlterField(
            model_name='document',
            name='name',
            field=models.CharField(max_length=255, verbose_name='name'),
        ),
        migrations.AlterField(
            model_name='document',
            name='slug',
            field=models.SlugField(max_length=255, verbose_name='slug'),
        ),
        migrations.AlterField(
            model_name='document',
            name='source',
            field=models.FileField(upload_to='reports', verbose_name='source'),
        ),
    ]
