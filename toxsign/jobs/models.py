import datetime, shutil, os
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import  User, Group
from django.conf import settings
from toxsign.tools.models import Tool
from django.contrib.postgres.fields import JSONField
from django.dispatch import receiver


# Create your models here.
class Job(models.Model):
    AVAILABLE_STATUS = (
        ('PENDING', 'PENDING'),
        ('RECEIVED', 'RECEIVED'),
        ('STARTED', 'STARTED'),
        ('FAILURE', 'FAILURE'),
        ('SUCCESS', 'SUCCESS'),
        ('REVOKED', 'REVOKED'),
        ('RETRY', 'RETRY'),
    )

    JOB_TYPE = (
        ('SYSTEM', 'SYSTEM'),
        ('TOOL', 'TOOL'),
        ('OTHER', 'OTHER'),
    )

    title = models.CharField(max_length=200)
    type = models.CharField(max_length=10, choices=JOB_TYPE, default="SYSTEM")
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.CASCADE, related_name='%(app_label)s_%(class)s_created_by')
    updated_at = models.DateTimeField(auto_now=True, null=True, verbose_name=("user"))
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.CASCADE, related_name='%(app_label)s_%(class)s_updated_by')
    status = models.CharField(max_length=10, choices=AVAILABLE_STATUS, default="PENDING")
    running_tool = models.ForeignKey(Tool, on_delete=models.CASCADE, related_name='jobs_asso_tools', blank=True, null=True)
    celery_task_id = models.CharField(max_length=250, blank=True, null=True)
    results = JSONField(null=True, blank=True, default=dict)

    def __str__(self):
        return self.title

@receiver(models.signals.post_delete, sender=Job)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    if instance.results and 'job_folder' in instance.results and instance.results['job_folder']:
        if os.path.exists(instance.results['job_folder']):
            shutil.rmtree(instance.results['job_folder'])
