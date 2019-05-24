from django.contrib.auth.models import AbstractUser
from django.db.models import CharField
from django.urls import reverse
from django.db import models
from django.contrib.auth.models import  User, Group
from django.conf import settings

from toxsign.projects.models import Project



class Study(models.Model):
    AVAILABLE_STATUS = (
        ('PRIVATE', 'Private'),
        ('PENDING', 'Pending'),
        ('PUBLIC', 'Public'),
    )
    STUDY_TYPE = (
        ('INTERVENTIONAL', 'Interventional'),
        ('OBSERVATIONAL', 'Observational'),
    )

    name = models.CharField(max_length=200)
    std_id = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.CASCADE, related_name='%(app_label)s_%(class)s_created_by')
    updated_at = models.DateTimeField(auto_now=True, null=True, verbose_name=("user"))
    status = models.CharField(max_length=20, choices=AVAILABLE_STATUS, default="PRIVATE")
    description = models.TextField("Description")
    experimental_design = models.TextField("Experimental design")
    study_type = models.CharField(max_length=50, choices=STUDY_TYPE, default="INTERVENTIONAL")
    results = models.TextField("Results")
    subClass = models.ForeignKey(Project, blank=True, null=True, on_delete=models.CASCADE, related_name='study_of')

    def __str__(self):
        return self.name
