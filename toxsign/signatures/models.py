from django.contrib.auth.models import AbstractUser
from django.db.models import CharField
from django.urls import reverse
from django.db import models
from django.contrib.auth.models import  User, Group
from django.conf import settings
from django.contrib.postgres.fields import JSONField

import os
import shutil
import time

from django.core.files import File
from toxsign.projects.models import Project
from toxsign.assays.models import Factor, Assay
from toxsign.genes.models import Gene
from toxsign.ontologies.models import Biological, Cell, CellLine, Chemical, Disease, Experiment, Species, Tissue

import tempfile
from django.db.models import Q
from toxsign.taskapp.celery import app

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
        # If file change
        if not index and (self.__old_up != self.up_gene_file_path or self.__old_down != self.down_gene_file_path or self.__old_all != self.interrogated_gene_file_path):
            index_genes.delay(self.id)
        self.__old_up = self.up_gene_file_path
        self.__old_down = self.down_gene_file_path
        self.__old_all = self.interrogated_gene_file_path


@app.task
def index_genes(signature_id):
    # Make sure the data is properly saved
    time.sleep(10)
    signature = Signature.objects.get(id=signature_id)
    # Moves files to proper folder
    new_path = "files/{}/{}/{}/{}/".format(signature.factor.assay.project.tsx_id, signature.factor.assay.tsx_id, signature.factor.tsx_id, signature.tsx_id)
    new_unix_path = settings.MEDIA_ROOT + "/" + new_path

    if not os.path.exists(new_unix_path):
        os.makedirs(new_unix_path)
    shutil.move(signature.up_gene_file_path.path, new_unix_path + "up_genes.txt")
    shutil.move(signature.down_gene_file_path.path, new_unix_path + "down_genes.txt")
    shutil.move(signature.interrogated_gene_file_path.path, new_unix_path + "all_genes.txt")
    shutil.move(signature.expression_values_file.path, new_unix_path + "processed_genes.txt")

    signature.up_gene_file_path.name = new_path + "up_genes.txt"
    signature.down_gene_file_path.name = new_path + "down_genes.txt"
    signature.interrogated_gene_file_path.name = new_path + "all_genes.txt"

    gene_dict = generate_values(signature)
    signature.expression_values = gene_dict
    write_gene_file(gene_dict, new_unix_path + "processed_genes.txt")
    signature.expression_values_file.name = new_path + "processed_genes.txt"


def generate_values(signature):
    # Starts from scratch
    values = {}
    gene_type = signature.gene_id
    # Starts with interrogated file to get them all (we will upload them later)
    if signature.interrogated_gene_file_path:
        values = prepare_values(values, signature.interrogated_gene_file_path.path, gene_type)
    if signature.up_gene_file_path:
        values = extract_values(values, signature.up_gene_file_path.path, gene_type, "1")
    if signature.down_gene_file_path:
        values = extract_values(values, signature.down_gene_file_path.path, gene_type, "-1")
    return values

def extract_values(values, file, gene_type, expression_value=None):

    genes = set()
    if not os.path.exists(file):
        return values
    with open(file, 'r') as f:
        for line in f:
            gene_id = line.strip()
            # Shoud not happen, but just in case
            if not gene_id in values:
                values[gene_id] = {'value': expression_value, 'homolog_id': 'NA'}
            else:
                values[gene_id]['value'] = expression_value

    return values

def prepare_values(values, file, gene_type):

    genes = set()
    processed_genes = set()

    if not os.path.exists(file):
        return values

    with open(file, 'r') as f:
        for line in f:
            gene_id = line.strip()
            genes.add(gene_id)

    if gene_type == "ENTREZ":
        for gene in Gene.objects.filter(gene_id__in=genes).values('gene_id', 'homolog_id'):
            values[gene['gene_id']] = {'value': 0, 'homolog_id': gene['homolog_id']}
        for missing_gene in genes - processed_genes:
            values[missing_gene] = {'value': 0, 'homolog_id': 'NA'}

    else:
        for gene in Gene.objects.filter(ensembl_id__in=genes).values('ensembl_id', 'homolog_id'):
            processed_genes.add(gene['ensembl_id'])
            values[gene['ensembl_id']] = {'value': 0, 'homolog_id': gene['homolog_id']}
        for missing_gene in genes - processed_genes:
            values[missing_gene] = {'value': 0, 'homolog_id': 'NA'}

    return values

def write_gene_file(gene_values, path):

    file = open(path, "w")
    for key, value in gene_values.items():
        file.write("{}\t{}\t{}\t".format(key, value["value"], value["homolog_id"]))
    file.close()

