from django.contrib.auth.models import AbstractUser
from django.db.models import CharField
from django.urls import reverse
from django.db import models
from django.contrib.auth.models import  User, Group
from django.conf import settings
from django.dispatch import receiver

import shutil
import os

from toxsign.projects.models import Project
from toxsign.ontologies.models import Biological, Cell, CellLine, Chemical, Disease, Experiment, Species, Tissue



class Assay(models.Model):
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
        ("NA", "Na"),
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
    EXPERIMENTAL_TYPE = (
        ('EXVIVO', 'Ex-vivo'),
        ('INVITRO', 'In-vitro'),
        ('INVIVO', 'In-vivo'),
        ("NA", "Na"),
        ("OTHER", "Other"),
    )

    name = models.CharField(max_length=500)
    tsx_id = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.CASCADE, related_name='%(app_label)s_%(class)s_created_by')
    updated_at = models.DateTimeField(auto_now=True, null=True, verbose_name=("user"))
    description = models.TextField("Description", blank=True)
    experimental_design = models.TextField("Experimental design", blank=True)
    additional_info = models.TextField("Additional information", blank=True)
    dev_stage = models.CharField(max_length=50, choices=DEVELOPPMENTAL_STAGE, default="NA")
    generation = models.CharField(max_length=10, choices=GENERATION, default="F0")
    sex_type = models.CharField(max_length=10, choices=SEX_TYPE, default="MALE")
    exp_type = models.CharField(max_length=10, choices=EXPERIMENTAL_TYPE, default="NA")
    project = models.ForeignKey(Project, blank=True, null=True, on_delete=models.CASCADE, related_name='assay_of')
    organism = models.ForeignKey(Species, blank=True, null=True, on_delete=models.CASCADE, related_name='assay_used_in')
    tissue = models.ForeignKey(Tissue, blank=True, null=True, on_delete=models.CASCADE, related_name='assay_used_in')
    cell = models.ForeignKey(Cell, blank=True, null=True, on_delete=models.CASCADE, related_name='assay_used_in')
    cell_line = models.ForeignKey(CellLine, blank=True, null=True, on_delete=models.CASCADE, related_name='assay_used_in')
    cell_line_slug = models.CharField(max_length=200, blank=True, null=True)
    results = models.TextField("Results", blank=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('assays:assay_detail', kwargs={"assid": self.tsx_id})

    # Override save method to auto increment tsx_id
    def save(self, *args, **kwargs):
        super(Assay, self).save(*args, **kwargs)
        self.tsx_id = "TSA" + str(self.id)
        super(Assay, self).save()

class Factor(models.Model):

    name = models.CharField(max_length=200)
    tsx_id = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.CASCADE, related_name='%(app_label)s_%(class)s_created_by')
    updated_at = models.DateTimeField(auto_now=True, null=True, verbose_name=("user"))
    assay = models.ForeignKey(Assay, blank=True, null=True, on_delete=models.CASCADE, related_name='factor_of')

    def __str__(self):
        return self.name

    # Redirect to assay page
    def get_absolute_url(self):
        return reverse('assays:factor_detail', kwargs={"facid": self.tsx_id})

    # Override save method to auto increment tsx_id
    def save(self, *args, **kwargs):
        super(Factor, self).save(*args, **kwargs)
        self.tsx_id = "TSF" + str(self.id)
        super(Factor, self).save()

class ChemicalsubFactor(models.Model):

    DOSE_UNIT = (
        ('NA', 'NA'),
        ('IC','IC'),
        ('EC','EC'),
        ('M','M'),
        ('mM','mM'),
        ('µM','µM'),
        ('nM','nM'),
        ('pM','pM'),
        ('fM','fM'),
        ('g/mL','g/mL'),
        ('mg/mL','mg/mL'),
        ('µg/mL','µg/mL'),
        ('ng/mL','ng/mL'),
        ('mg/kg','mg/kg'),
        ('µg/kg','µg/kg'),
        ('ng/kg','ng/kg'),
        ('ng/g lipid','ng/g lipid'),
        ('ng/g creatinine','ng/g creatinine'),
    )

    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.CASCADE, related_name='%(app_label)s_%(class)s_created_by')
    updated_at = models.DateTimeField(auto_now=True, null=True, verbose_name=("user"))
    factor = models.ForeignKey(Factor, on_delete=models.CASCADE, related_name='chemical_subfactor_of')
    chemical = models.ForeignKey(Chemical, blank=True, null=True, on_delete=models.CASCADE, related_name='chemical_subfactor_used_in')
    chemical_slug = models.CharField(max_length=500, blank=True)
    route = models.CharField(max_length=200, blank=True)
    vehicule = models.CharField(max_length=200, blank=True)
    dose_value = models.FloatField(null=True, blank=True, default=None)
    dose_unit = models.CharField(max_length=50, choices=DOSE_UNIT, default="M")
    exposure_time = models.FloatField(null=True, blank=True, default=None)
    exposure_frequencie = models.CharField(max_length=200, blank=True)
    additional_info = models.TextField("Additional information")

    # Redirect to factor page
    def get_absolute_url(self):
        return reverse('assays:factor_detail', kwargs={"facid": self.factor.tsx_id})

@receiver(models.signals.pre_delete, sender=Assay)
def auto_delete_assay_on_delete(sender, instance, **kwargs):
    # Delete the folder
    if not instance.project:
        return

    local_path = "{}/{}/".format(instance.project.tsx_id, instance.tsx_id)
    unix_path = settings.MEDIA_ROOT + "/files/" + local_path
    if(os.path.exists(unix_path)):
        shutil.rmtree(unix_path)

@receiver(models.signals.pre_delete, sender=Factor)
def auto_delete_factor_on_delete(sender, instance, **kwargs):
    # Delete the folder
    if not instance.assay or not instance.assay.project:
        return

    local_path = "{}/{}/{}/".format(instance.assay.project.tsx_id, instance.assay.tsx_id, instance.tsx_id)
    unix_path = settings.MEDIA_ROOT + "/files/" + local_path
    if(os.path.exists(unix_path)):
        shutil.rmtree(unix_path)
