# Generated by Django 2.0.3 on 2018-03-21 20:10

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_courier', '0005_contact_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='template',
            name='notification',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                to='django_courier.Notification',
                verbose_name='notification'),
        ),
    ]
