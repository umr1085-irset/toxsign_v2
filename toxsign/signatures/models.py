from django.contrib.auth.models import AbstractUser
from django.db.models import CharField
from django.urls import reverse
from django.db import models
from django.contrib.auth.models import  User, Group
from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.dispatch import receiver

import os
import shutil
import time

from django.core.files import File
from toxsign.assays.models import Factor, Assay
from toxsign.genes.models import Gene
from toxsign.ontologies.models import Biological, Cell, CellLine, Chemical, Disease, Experiment, Species, Tissue

import tempfile
from django.db.models import Q
from toxsign.taskapp.celery import app

from toxsign.scripts.data import setup_files

class Signature(models.Model):
    DEVELOPPMENTAL_STAGE = (
        ("FETAL", 'Fetal'),
        ("EMBRYONIC", "Embryonic"),
        ("LARVA", "Larva"),
        ("NEONATAL", "Neo-natal"),
        ("JUVENILE", "Juvenile"),
        ("PREPUBERTAL", "Prepubertal"),
        ("ADULTHOOD", "Adulthood"),
        ("ELDERLY", "Elderly"),
        ("NA", "Na"),
        ("OTHER", "Other"),
    )
    GENERATION = (
        ('F0', 'F0'),
        ('F1', 'F1'),
        ('F2', 'F2'),
        ('F3', 'F3'),
        ('F4', 'F4'),
        ('F5', 'F5'),
    )
    SEX_TYPE = (
        ('MALE', 'Male'),
        ('FEMALE', 'Female'),
        ('BOTH', 'Both'),
        ("NA", "Na"),
        ("OTHER", "Other"),
    )

    SIGNATURE_TYPE = (
        ('GENOMICS', 'Genomics'),
        ('METABOLOMICS', 'Metabolomics'),
    )

    GENE_ID = (
        ('ENTREZ', 'Entrez genes'),
        ('ENSEMBL', 'Ensembl'),
    )

    EXPERIMENTAL_TYPE = (
        ('EXVIVO', 'Ex-vivo'),
        ('INVITRO', 'In-vitro'),
        ('INVIVO', 'In-vivo'),
        ("NA", "Na"),
        ("OTHER", "Other"),
    )

    name = models.CharField(max_length=200)
    tsx_id = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.CASCADE, related_name='%(app_label)s_%(class)s_created_by')
    updated_at = models.DateTimeField(auto_now=True, null=True, verbose_name=("user"))
    signature_type = models.CharField(max_length=20, choices=SIGNATURE_TYPE, default="GENOMICS")
    phenotype_description = models.TextField("Phenotype description")
    experimental_design = models.TextField("Experimental design")
    dev_stage = models.CharField(max_length=50, choices=DEVELOPPMENTAL_STAGE, default="NA")
    generation = models.CharField(max_length=10, choices=GENERATION, default="F0")
    sex_type = models.CharField(max_length=10, choices=SEX_TYPE, default="MALE")
    exp_type = models.CharField(max_length=10, choices=EXPERIMENTAL_TYPE, default="NA")
    factor = models.ForeignKey(Factor, blank=True, null=True, on_delete=models.CASCADE, related_name='signature_of_of')
    organism = models.ManyToManyField(Species, blank=True, related_name='signature_used_in')
    tissue = models.ManyToManyField(Tissue, blank=True, related_name='signature_used_in')
    cell = models.ManyToManyField(Cell, blank=True, related_name='signature_used_in')
    cell_line = models.ManyToManyField(CellLine, blank=True, related_name='signature_used_in')
    chemical = models.ManyToManyField(Chemical, blank=True, related_name='signature_used_in')
    chemical_slug = models.CharField(max_length=200)
    disease = models.ManyToManyField(Disease, blank=True, related_name='signature_used_in')
    technology = models.ManyToManyField(Experiment, blank=True, related_name='signature_used_in')
    technology_slug = models.CharField(max_length=200)
    platform = models.CharField(max_length=200)
    control_sample_number = models.FloatField(null=True, blank=True, default=None)
    treated_sample_number = models.FloatField(null=True, blank=True, default=None)
    pvalue = models.FloatField(null=True, blank=True, default=None)
    cutoff = models.FloatField(null=True, blank=True, default=None)
    statistical_processing = models.TextField("Statistical processing")
    # Might need to move them to a proper folder
    up_gene_file_path = models.FileField(upload_to='files/', blank=True)
    down_gene_file_path = models.FileField(upload_to='files/', blank=True)
    interrogated_gene_file_path = models.FileField(upload_to='files/', blank=True)
    additional_file_path = models.FileField(upload_to='files/', blank=True)
    gene_id = models.CharField(max_length=50, choices=GENE_ID, default="ENTREZ")
    expression_values = JSONField(null=True, blank=True, default=dict)
    expression_values_file = models.FileField(upload_to='files/', blank=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('signatures:detail', kwargs={"sigid": self.tsx_id})

    def __init__(self, *args, **kwargs):
        super(Signature, self).__init__(*args, **kwargs)
        self.__old_up = self.up_gene_file_path
        self.__old_down = self.down_gene_file_path
        self.__old_all = self.interrogated_gene_file_path
        self.__old_add = self.additional_file_path

    # Override save method to auto increment tsx_id
    def save(self, *args, **kwargs):
        index = kwargs.pop('index', False)
        super(Signature, self).save(*args, **kwargs)
        # Hacky Hacky
        if not self.expression_values_file:
            temp_file = tempfile.TemporaryFile()
            self.expression_values_file.save("temp", File(temp_file), save=True)
            temp_file.close()
        if not self.tsx_id:
            self.tsx_id = "TSS" + str(self.id)
        super(Signature, self).save()

        file_changed = False
        need_index = False

        if self.__old_add != self.additional_file_path:
            file_changed = True

        if not index and (self.__old_up != self.up_gene_file_path or self.__old_down != self.down_gene_file_path or self.__old_all != self.interrogated_gene_file_path):
            need_index = True

        if file_changed or need_index:
            setup_files.delay(self.id, need_index, file_changed)

        self.__old_up = self.up_gene_file_path
        self.__old_down = self.down_gene_file_path
        self.__old_all = self.interrogated_gene_file_path
        self.__old_add = self.additional_file_path

@receiver(models.signals.post_delete, sender=Signature)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    # Delete the folder
    if(instance.expression_values_file):
        folder_path = os.path.dirname(instance.expression_values_file.path)
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)


