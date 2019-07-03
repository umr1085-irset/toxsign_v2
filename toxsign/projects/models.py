from django.contrib.auth.models import AbstractUser
from django.db.models import CharField
from django.urls import reverse
from django.db import models
from django.contrib.auth.models import  User, Group
from django.conf import settings


class Project(models.Model):
    AVAILABLE_STATUS = (
        ('PRIVATE', 'Private'),
        ('PENDING', 'Pending'),
        ('PUBLIC', 'Public'),
    )
    name = models.CharField(max_length=200)
    tsx_id = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.CASCADE, related_name='%(app_label)s_%(class)s_created_by')
    updated_at = models.DateTimeField(auto_now=True, null=True, verbose_name=("user"))
    status = models.CharField(max_length=20, choices=AVAILABLE_STATUS, default="PRIVATE")
    description = models.TextField("description")

    def __str__(self):
        return self.name

    # Override save method to auto increment tsx_id
    def save(self, *args, **kwargs):
        super(Project, self).save(*args, **kwargs)
        self.tsx_id = "TSP" + str(self.id)
        super(Project, self).save(*args, **kwargs)
