# Generated by Django 2.0.13 on 2019-07-17 10:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0009_alter_user_last_name_max_length'),
        ('projects', '0003_auto_20190708_0834'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='edit_groups',
            field=models.ManyToManyField(blank=True, related_name='edit_access_to', to='auth.Group'),
        ),
        migrations.AddField(
            model_name='project',
            name='read_groups',
            field=models.ManyToManyField(blank=True, related_name='read_access_to', to='auth.Group'),
        ),
    ]