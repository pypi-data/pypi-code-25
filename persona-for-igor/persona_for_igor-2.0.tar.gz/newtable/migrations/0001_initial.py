# Generated by Django 2.0.4 on 2018-04-16 13:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('personas', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254, unique=True)),
            ],
            options={
                'db_table': 'accounts',
            },
        ),
        migrations.CreateModel(
            name='Hub',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hub_name', models.CharField(default='', max_length=100)),
                ('api_user_name', models.CharField(default='', max_length=255)),
                ('api_password', models.CharField(default='', max_length=255)),
                ('account_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='newtable.Account')),
            ],
            options={
                'db_table': 'hubs',
            },
        ),
        migrations.CreateModel(
            name='PersonasToHubs',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hub', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='newtable.Hub')),
                ('personas', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='personas.Personas')),
            ],
        ),
    ]
