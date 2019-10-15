import sys
from django.contrib.auth.models import AbstractUser
from django.db.models import CharField
from django.urls import reverse
from django.db import models
from django.contrib.auth.models import  User, Group
from django.conf import settings
from guardian.shortcuts import assign_perm, remove_perm, get_group_perms, get_user_perms
from django.db.models.signals import m2m_changed
from django.dispatch import receiver

import subprocess
import os
import shutil

from toxsign.superprojects.models import Superproject
from toxsign.taskapp.celery import app

class Project(models.Model):
    AVAILABLE_STATUS = (
        ('PRIVATE', 'Private'),
        ('PENDING', 'Pending'),
        ('PUBLIC', 'Public'),
    )

    PROJECT_TYPE = (
        ('INTERVENTIONAL', 'Interventional'),
        ('OBSERVATIONAL', 'Observational'),
    )

    name = models.CharField(max_length=200, unique=True)
    tsx_id = models.CharField(max_length=200)
    superproject = models.ForeignKey(Superproject, blank=True, null=True, on_delete=models.SET_NULL, related_name='project_of')
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.CASCADE, related_name='%(app_label)s_%(class)s_created_by')
    updated_at = models.DateTimeField(auto_now=True, null=True, verbose_name=("user"))
    read_groups = models.ManyToManyField(Group, blank=True, related_name='read_access_to')
    edit_groups = models.ManyToManyField(Group, blank=True, related_name='edit_access_to')
    status = models.CharField(max_length=20, choices=AVAILABLE_STATUS, default="PRIVATE")
    description = models.TextField("description", blank=True)
    experimental_design = models.TextField("Experimental design", blank=True)
    project_type = models.CharField(max_length=50, choices=PROJECT_TYPE, default="INTERVENTIONAL")
    results = models.TextField("Results", blank=True)

    class Meta:
        permissions = (('view_project', 'View project'),)
        default_permissions = ('add', 'change', 'delete')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('projects:detail', kwargs={"prjid": self.tsx_id})

    def __init__(self, *args, **kwargs):
        super(Project, self).__init__(*args, **kwargs)
        self.initial_owner = self.created_by
        self.initial_status = self.status

    # Override save method to auto increment tsx_id
    # Also set permissions for owner on item
    def save(self, *args, **kwargs):
        super(Project, self).save(*args, **kwargs)
        self.tsx_id = "TSP" + str(self.id)
        super(Project, self).save()
        change_permission_owner(self)
        # if status was changed to public. What if it went from public to private?
        if self.initial_status != self.status and self.status == "PUBLIC":
            change_status.delay(self.id)


# Need to add some checks (or catch exception) in case there is a disconnect between existing perm and groups
@receiver(m2m_changed, sender=Project.read_groups.through)
def update__permissions_read(sender, instance, action, **kwargs):
    if instance.read_groups.all():
        if action == 'pre_remove':
            for group in instance.read_groups.all():
                if 'view_project' in get_group_perms(group, instance):
                    remove_perm('view_project', group, instance)
        if action == 'post_add':
            for group in instance.read_groups.all():
                if 'view_project' not in get_group_perms(group, instance):
                    assign_perm('view_project', group, instance)

@receiver(m2m_changed, sender=Project.edit_groups.through)
def update__permissions_write(sender, instance, action, **kwargs):
    if instance.edit_groups.all():
        if action == 'pre_remove':
            for group in instance.edit_groups.all():
                if 'view_project' in get_group_perms(group, instance):
                    remove_perm('change_project', group, instance)
        if action == 'post_add':
            for group in instance.edit_groups.all():
                if 'view_project' not in get_group_perms(group, instance):
                    assign_perm('change_project', group, instance)

def change_permission_owner(self):
    owner_permissions = ['view_project', 'change_project', 'delete_project']

    if self.initial_owner:
               # If update, remove permission, else do nothing
        if self.initial_owner != self.created_by:
            initial_owner_permission = get_user_perms(self.initial_owner, self)
            for permission in owner_permissions:
                if permission in initial_owner_permission:
                    remove_perm(permission, self.initial_owner, self)

    user_permissions = get_user_perms(self.created_by, self)
    for permission in owner_permissions:
        if permission not in user_permissions:
            assign_perm(permission, self.created_by, self)


@app.task(bind=True)
def change_status(self, project_id):
    # Import here to avoid cyclical import
    from toxsign.signatures.models import Signature
    temp_dir_path = "/app/tools/job_dir/temp/" + self.request.id + "/"

    if os.path.exists(temp_dir_path):
        print("Folder {} already exists: stopping..".format(temp_dir_path))

    # Should test if this project has signature. No point in recalculating if nothing is new
    project_sig = Signature.objects.filter(factor__assay__project__id=project_id)
    if not project_sig.exists():
        return

    public_sigs = Signature.objects.filter(factor__assay__project__status="PUBLIC")
    if not public_sigs.exists():
        return

    os.mkdir(temp_dir_path)

    for sig in public_sigs:
        if sig.expression_values_file:
            shutil.copy2(sig.expression_values_file.path, temp_dir_path)
    if os.path.exists("/app/tools/admin_data/public.RData"):
        shutil.copy2("/app/tools/admin_data/public.RData", temp_dir_path + "public.RData.old")

    # Need to check the result...
    subprocess.run(['/bin/bash', '/app/tools/make_public/make_public.sh', temp_dir_path])
