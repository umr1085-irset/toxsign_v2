# Generated by Django 2.0.13 on 2019-07-09 13:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('signatures', '0002_auto_20190708_0834'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='signature',
            name='status',
        ),
    ]
