import datetime
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import  User, Group
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.apps import apps
import os

from toxsign.scripts.data import setup_cluster

from django.contrib.postgres.fields import JSONField

from functools import partial

def get_upload_path(dist_type, instance, filename):

    path =  os.path.join("clusters/{}/{}/".format(instance.distance_method, instance.cluster_id), dist_type)
    return path


class Cluster(models.Model):

    DISTANCE_METHODS = (
        ('euclidean', 'Euclidean'),
        ('correlation', 'Correlation'),
    )

    cluster_id = models.CharField(max_length=5)
    distance_method = models.CharField(max_length=20, choices=DISTANCE_METHODS)

    conditions_file = models.FileField(upload_to=partial(get_upload_path, "cluster.txt"))
    signature_file = models.FileField(upload_to=partial(get_upload_path, "signature.txt"), blank=True)
    chemical_enrichment_file = models.FileField(upload_to=partial(get_upload_path, "chem2enr.csv"), blank=True)
    gene_enrichment_file = models.FileField(upload_to=partial(get_upload_path, "gene2enr.csv"), blank=True)
    signature = JSONField(null=True, blank=True, default=dict)
    conditions = JSONField(null=True, blank=True, default=dict)

    def __str__(self):
        return self.cluster_id

    def __init__(self, *args, **kwargs):
        super(Cluster, self).__init__(*args, **kwargs)
        self.__old_condition = self.conditions_file
        self.__old_signature = self.signature_file

    def save(self, *args, **kwargs):
        force = kwargs.pop('force', False)
        super(Cluster, self).save(*args, **kwargs)

        need_process = False

        if (self.__old_condition != self.conditions_file or self.__old_signature != self.signature_file):
            need_process = True
        if force:
            need_process = True

        if need_process:
            task = setup_cluster.delay(self.id)

        self.__old_condition = self.conditions_file
        self.__old_signature = self.signature_file
