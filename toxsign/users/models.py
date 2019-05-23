from django.contrib.auth.models import AbstractUser
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
