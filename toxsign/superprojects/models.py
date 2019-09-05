import sys
from django.contrib.auth.models import AbstractUser
from django.db.models import CharField
from django.urls import reverse
from django.db import models
from django.contrib.auth.models import  User, Group
from django.conf import settings

class Superproject(models.Model):
    name = models.CharField(max_length=200, unique=True)
    tsx_id = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.CASCADE, related_name='%(app_label)s_%(class)s_created_by')
    updated_at = models.DateTimeField(auto_now=True, null=True, verbose_name=("user"))
    description = models.TextField("description")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('superprojects:detail', kwargs={"spjid": self.tsx_id})

    def __init__(self, *args, **kwargs):
        super(Superproject, self).__init__(*args, **kwargs)
        self.initial_owner = self.created_by

    # Override save method to auto increment tsx_id
    # Also set permissions for owner on item
    def save(self, *args, **kwargs):
        super(Superproject, self).save(*args, **kwargs)
        self.tsx_id = "TSSP" + str(self.id)
        super(Superproject, self).save()
