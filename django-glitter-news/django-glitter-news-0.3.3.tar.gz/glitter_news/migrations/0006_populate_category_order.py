# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def order_categories(apps, schema_editor):
    Category = apps.get_model('glitter_news', 'Category')
    for index, category in enumerate(Category.objects.order_by('title')):
        category.order = index + 1
        category.save()


def reset_category_order(apps, schema_editor):
    Category = apps.get_model('glitter_news', 'Category')
    Category.objects.update(order=0)


class Migration(migrations.Migration):

    dependencies = [
        ('glitter_news', '0005_add_sortable'),
    ]

    operations = [
        migrations.RunPython(order_categories, reset_category_order),
    ]
