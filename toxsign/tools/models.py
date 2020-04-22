import datetime
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import  User, Group
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.postgres.fields import JSONField
from django.apps import apps

from django.dispatch import receiver

import os, shutil

def get_model_upload_path(instance, filename):

    path =  os.path.join("jobs/admin/{}/".format(instance.computer_name), "model.h5")
    return path

def get_association_upload_path(instance, filename):

    path =  os.path.join("jobs/admin/{}/".format(instance.computer_name), "association_matrix.tsv")
    return path

# Create your models here.
class Tag(models.Model):
    word        = models.CharField(max_length=35)
    slug        = models.CharField(max_length=250)
    created_at  = models.DateTimeField(auto_now_add=False)

    def __str__(self):
        return self.word

class ArgumentType(models.Model):

    type = models.CharField(max_length=20, default="TEXT")

    def __str__(self):
        return self.type

class Category(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField("description")

    def __str__(self):
        return self.name

class Tool(models.Model):
    AVAILABLE_STATUS = (
        ('STABLE', 'Stable'),
        ('DEVELOPPMENT', 'Developpment'),
        ('OUTDATED', 'Outdated'),
    )

    TYPES = (
        ('LOCAL', 'Local link'),
        ('COMPUTED', 'Local job'),
        ('REMOTE', 'Remote tool'),
    )

    name = models.CharField(max_length=200)
    type = models.CharField(max_length=20, choices=TYPES, default="LOCAL")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='category_of')
    short_description = models.CharField(max_length=200)
    description = models.TextField("description")
    status = models.CharField(max_length=20, choices=AVAILABLE_STATUS, default="DEVELOPPMENT")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.CASCADE, related_name='%(app_label)s_%(class)s_created_by')
    icon = models.ImageField(upload_to='tools/', null=True, verbose_name="")
    visuel = models.ImageField(upload_to='tools/', null=True, verbose_name="")
    link = models.CharField(max_length=200,  blank=True, null=True)
    form_name = models.CharField(max_length=100, default='default_form', blank=True, null=True)
    script_file = models.CharField(max_length=250, blank=True, null=True)
    custom_result_link = models.CharField(max_length=250, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated_at = models.DateTimeField(auto_now=True, null=True, verbose_name=("user"))
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.CASCADE, related_name='%(app_label)s_%(class)s_updated_by')
    tags = models.ManyToManyField(Tag, related_name='tool_tag_description')
    argument_types = models.ManyToManyField(ArgumentType, through='Argument')

    def __str__(self):
        return self.name

class Argument(models.Model):
    tool = models.ForeignKey(Tool, on_delete=models.CASCADE, related_name='arguments')
    argument_type = models.ForeignKey(ArgumentType, on_delete=models.CASCADE)
    label = models.CharField(max_length=200)
    parameter = models.CharField(max_length=10, blank=True, null=True)
    multiple = models.BooleanField(default=False)
    user_filled = models.BooleanField(default=True)
    optional = models.BooleanField(default=True)
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ('order',)

class PredictionModel(models.Model):

    name = models.CharField(max_length=200)
    computer_name = models.CharField(max_length=50)
    description = models.TextField("description", blank=True, null=True)
    model_file = models.FileField(upload_to=get_model_upload_path)
    association_matrix = models.FileField(upload_to=get_association_upload_path)
    parameters = JSONField(null=True, blank=True, default=dict)

    def __str__(self):
        return self.name

@receiver(models.signals.pre_delete, sender=PredictionModel)
def auto_delete_signature_on_delete(sender, instance, **kwargs):
    # Delete the folder
    if instance.computer_name:
        local_path = os.path.join(settings.MEDIA_ROOT, "jobs/admin/{}/".format(instance.computer_name))
        if(os.path.exists(local_path)):
            shutil.rmtree(local_path)
