# Generated by Django 2.0.13 on 2019-11-05 10:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0002_auto_20191023_0723'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='type',
            field=models.CharField(choices=[('SYSTEM', 'SYSTEM'), ('TOOL', 'TOOL'), ('OTHER', 'OTHER')], default='SYSTEM', max_length=10),
        ),
    ]