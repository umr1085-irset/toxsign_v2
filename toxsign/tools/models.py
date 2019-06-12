import datetime
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import  User, Group
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator


# Create your models here.

class Tag(models.Model):
    word        = models.CharField(max_length=35)
    slug        = models.CharField(max_length=250)
    created_at  = models.DateTimeField(auto_now_add=False)

    def __str__(self):
        return self.word

class Tool(models.Model):
    AVAILABLE_STATUS = (
        ('STABLE', 'Stable'),
        ('DEVELOPPMENT', 'Developpment'),
        ('OUTDATED', 'Outdated'),
    )

    name = models.CharField(max_length=200)
    html_name = models.CharField(max_length=200,  blank=True, null=True)
    short_description = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField("description")
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.CASCADE, related_name='%(app_label)s_%(class)s_created_by')
    updated_at = models.DateTimeField(auto_now=True, null=True, verbose_name=("user"))
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.CASCADE, related_name='%(app_label)s_%(class)s_updated_by')
    status = models.CharField(max_length=20, choices=AVAILABLE_STATUS, default="DEVELOPPMENT")
    command_line = models.CharField(max_length=250, null=True)
    path = models.CharField(max_length=250,null=True)
    script_name = models.CharField(max_length=250,null=True)
    visuel = models.ImageField(upload_to='tools/', null=True, verbose_name="")
    tags = models.ManyToManyField(Tag, related_name='tool_tag_description')

    def __str__(self):
        return self.name