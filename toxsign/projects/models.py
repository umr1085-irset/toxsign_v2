import sys
from django.contrib.auth.models import AbstractUser
from django.db.models import CharField
from django.urls import reverse
from django.db import models
from django.contrib.auth.models import  User, Group
from django.conf import settings
from guardian.shortcuts import assign_perm, remove_perm, get_group_perms
from django.db.models.signals import m2m_changed
from django.dispatch import receiver

class Project(models.Model):
    AVAILABLE_STATUS = (
        ('PRIVATE', 'Private'),
        ('PENDING', 'Pending'),
        ('PUBLIC', 'Public'),
    )
    name = models.CharField(max_length=200, unique=True)
    tsx_id = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.CASCADE, related_name='%(app_label)s_%(class)s_created_by')
    updated_at = models.DateTimeField(auto_now=True, null=True, verbose_name=("user"))
    read_groups = models.ManyToManyField(Group, blank=True, related_name='read_access_to')
    edit_groups = models.ManyToManyField(Group, blank=True, related_name='edit_access_to')
    status = models.CharField(max_length=20, choices=AVAILABLE_STATUS, default="PRIVATE")
    description = models.TextField("description")


    class Meta:
        permissions = (('view_project', 'View project'),)
        default_permissions = ('add', 'change', 'delete')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('projects:detail', kwargs={"prjid": self.tsx_id})

    # Override save method to auto increment tsx_id
    def save(self, *args, **kwargs):
        super(Project, self).save(*args, **kwargs)
        self.tsx_id = "TSP" + str(self.id)
        super(Project, self).save()

# Need to add some checks (or catch exception) in case there is a disconnect between existing perm and groups
@receiver(m2m_changed, sender=Project.read_groups.through)
def update__permissions_test(sender, instance, action, **kwargs):
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
def update__permissions(sender, instance, action, **kwargs):
    if instance.edit_groups.all():
        if action == 'pre_remove':
            current_perms = get_groups_with_perms()
            for group in instance.edit_groups.all():
                remove_perm('edit_project', group, instance)
        if action == 'post_add':
            assign_perm('edit_project', instance.edit_groups.all(), instance)
