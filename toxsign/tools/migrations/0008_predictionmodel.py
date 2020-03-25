# Generated by Django 2.0.13 on 2020-02-28 16:04

from django.db import migrations, models
import toxsign.tools.models


class Migration(migrations.Migration):

    dependencies = [
        ('tools', '0007_auto_20191023_1058'),
    ]

    operations = [
        migrations.CreateModel(
            name='PredictionModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('computer_name', models.CharField(max_length=50)),
                ('description', models.TextField(blank=True, null=True, verbose_name='description')),
                ('model_file', models.FileField(upload_to=toxsign.tools.models.get_model_upload_path)),
                ('association_matrix', models.FileField(upload_to=toxsign.tools.models.get_association_upload_path)),
            ],
        ),
    ]