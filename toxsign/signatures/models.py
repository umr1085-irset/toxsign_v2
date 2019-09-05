from django.contrib.auth.models import AbstractUser
from django.db.models import CharField
from django.urls import reverse
from django.db import models
from django.contrib.auth.models import  User, Group
from django.conf import settings

from toxsign.projects.models import Project
from toxsign.assays.models import Assay
from toxsign.assays.models import Factor, Assay
from toxsign.ontologies.models import Biological, Cell, CellLine, Chemical, Disease, Experiment, Species, Tissue



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
    up_gene_file_path = models.CharField(max_length=500)
    down_gene_file_path = models.CharField(max_length=500)
    interrogated_gene_file_path = models.CharField(max_length=500)
    additional_file_path = models.CharField(max_length=500)
    gene_id = models.CharField(max_length=50, choices=GENE_ID, default="ENTREZ")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('signatures:detail', kwargs={"sigid": self.tsx_id})

    # Override save method to auto increment tsx_id
    def save(self, *args, **kwargs):
        super(Signature, self).save(*args, **kwargs)
        self.tsx_id = "TSS" + str(self.id)
        super(Signature, self).save()
