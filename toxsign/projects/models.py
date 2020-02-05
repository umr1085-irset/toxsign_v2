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
from toxsign.scripts.data import change_status


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

    name = models.CharField(max_length=200)
    tsx_id = models.CharField(max_length=200)
    pubmed_id = models.CharField(max_length=200, blank=True, null=True)
    cross_link = models.TextField("cross_link", blank=True, null=True)
    superproject = models.ForeignKey(Superproject, blank=True, null=True, on_delete=models.SET_NULL, related_name='project_of')
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.CASCADE, related_name='%(app_label)s_%(class)s_created_by')
    updated_at = models.DateTimeField(auto_now=True, null=True, verbose_name=("user"))
    read_groups = models.ManyToManyField(Group, blank=True, related_name='read_access_to')
    edit_groups = models.ManyToManyField(Group, blank=True, related_name='edit_access_to')
    status = models.CharField(max_length=20, choices=AVAILABLE_STATUS, default="PRIVATE")
    description = models.TextField("description", blank=True,null=True)
    project_type = models.CharField(max_length=50, choices=PROJECT_TYPE, default="INTERVENTIONAL")

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
        force = kwargs.pop('force', False)
        super(Project, self).save(*args, **kwargs)
        self.tsx_id = "TSP" + str(self.id)
        super(Project, self).save()
        change_permission_owner(self)
        # if status was changed to public. What if it went from public to private?
        if not force and self.initial_status != self.status and self.status == "PUBLIC":
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
                if 'change_project' in get_group_perms(group, instance):
                    remove_perm('change_project', group, instance)
        if action == 'post_add':
            for group in instance.edit_groups.all():
                if 'change_project' not in get_group_perms(group, instance):
                    assign_perm('change_project', group, instance)

@receiver(models.signals.pre_delete, sender=Project)
def auto_delete_project_on_delete(sender, instance, **kwargs):
    # Delete the folder
    local_path = "{}/".format(instance.tsx_id)
    unix_path = settings.MEDIA_ROOT + "/files/" + local_path
    if(os.path.exists(unix_path)):
        shutil.rmtree(unix_path)

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
