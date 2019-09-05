from django.contrib.auth.models import AbstractUser
from django.db.models import CharField
from django.urls import reverse
from django.db import models
from django.contrib.auth.models import  User, Group
from django.conf import settings

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

    name = models.CharField(max_length=200)
    tsx_id = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.CASCADE, related_name='%(app_label)s_%(class)s_created_by')
    updated_at = models.DateTimeField(auto_now=True, null=True, verbose_name=("user"))
    additional_info = models.TextField("Additional information")
    experimental_design = models.TextField("Experimental design")
    dev_stage = models.CharField(max_length=50, choices=DEVELOPPMENTAL_STAGE, default="NA")
    generation = models.CharField(max_length=10, choices=GENERATION, default="F0")
    sex_type = models.CharField(max_length=10, choices=SEX_TYPE, default="MALE")
    exp_type = models.CharField(max_length=10, choices=EXPERIMENTAL_TYPE, default="NA")
    project = models.ForeignKey(Project, blank=True, null=True, on_delete=models.CASCADE, related_name='assay_of')
    organism = models.ForeignKey(Species, blank=True, null=True, on_delete=models.CASCADE, related_name='assay_used_in')
    tissue = models.ForeignKey(Tissue, blank=True, null=True, on_delete=models.CASCADE, related_name='assay_used_in')
    cell = models.ForeignKey(Cell, blank=True, null=True, on_delete=models.CASCADE, related_name='assay_used_in')
    cell_line = models.ForeignKey(CellLine, blank=True, null=True, on_delete=models.CASCADE, related_name='assay_used_in')

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
    CHEMICAL_TYPE = (
        ('CHEMICAL', 'Chemical'),
        ('BIOLOGICAL', 'Biological'),
        ('PHYSICAL', 'Physical'),
    )

    DOSE_UNIT = (
        ('M','M'),
        ('mM','mM'),
        ('µM','µM'),
        ('g/mL','g/mL'),
        ('mg/mL','mg/mL'),
        ('µg/mL','µg/mL'),
        ('ng/mL','ng/mL'),
        ('mg/kg','mg/kg'),
        ('µg/kg','µg/kg'),
        ('µg/kg','µg/kg'),
        ('ng/kg','ng/kg'),
        ('ng/g lipid','ng/g lipid'),
        ('ng/g creatinine','ng/g creatinine'),
    )

    name = models.CharField(max_length=200)
    tsx_id = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.CASCADE, related_name='%(app_label)s_%(class)s_created_by')
    updated_at = models.DateTimeField(auto_now=True, null=True, verbose_name=("user"))
    chemical = models.ForeignKey(Chemical, blank=True, null=True, on_delete=models.CASCADE, related_name='factor_used_in')
    chemical_slug = models.CharField(max_length=200)
    factor_type = models.CharField(max_length=50, choices=CHEMICAL_TYPE, default="CHEMICAL")
    route = models.CharField(max_length=200)
    vehicule = models.CharField(max_length=200)
    dose_value = models.FloatField(null=True, blank=True, default=None)
    dose_unit = models.CharField(max_length=50, choices=DOSE_UNIT, default="M")
    exposure_time = models.FloatField(null=True, blank=True, default=None)
    exposure_frequencie = models.CharField(max_length=200)
    additional_info = models.TextField("Additional information")
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
