from django.contrib.auth.models import Group
from django.db.models import CharField
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.db import models
from toxsign.users.models import User

from django.db.models.signals import post_save
from django.dispatch import receiver


class Ownership(models.Model):

    group = models.OneToOneField(Group, on_delete=models.CASCADE)
    owner = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE, related_name='owner_of')


@receiver(post_save, sender=Group)
def create_custom_group(sender, instance, created, **kwargs):
    if created:
        Ownership.objects.create(group=instance)

@receiver(post_save, sender=Group)
def save_custom_group(sender, instance, **kwargs):
        if not hasattr(instance, 'customgroup'):
            Ownership.objects.create(group=instance)
        else:
            instance.ownership.save()
