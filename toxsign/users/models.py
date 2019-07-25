
from django.contrib.auth.models import AbstractUser, Group
from django.db.models import CharField
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from toxsign.projects.models import Project
from django.db import models



class User(AbstractUser):

    # First Name and Last Name do not cover name patterns
    # around the globe.
    name = CharField(_("Name of User"), blank=True, max_length=255)
    last_name = CharField(_("Last name of User"), blank=True, max_length=255)
    institut = CharField(_("User institut"), blank=True, max_length=255)
    projects = models.ManyToManyField(Project, related_name='projects')

    def get_absolute_url(self):
        return reverse("users:detail", kwargs={"username": self.username})


# Might be a better way to implement this if we need other types..
class Notification(models.Model):

    NOTIFICATION_TYPES = [
        ('GROUP', 'Add user to group'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_notifications')
    message =  models.TextField("description")
    group = models.ForeignKey(Group, blank=True, null=True, on_delete=models.CASCADE, related_name='add_notifications')
    type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
