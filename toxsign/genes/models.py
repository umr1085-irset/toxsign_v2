import datetime
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import  User, Group
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.apps import apps

class Gene(models.Model):

    gene_id =  models.CharField(max_length=50)
    tax_id =  models.CharField(max_length=50, blank=True)
    symbol =  models.CharField(max_length=50, blank=True)
    synonyms =  models.TextField(blank=True)
    description =  models.TextField(blank=True)
    homolog_id =  models.CharField(max_length=50, blank=True)
    ensembl_id =  models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.gene_id

class Pathway(models.Model):

    name = models.CharField(max_length=200)
    pathway_id = models.CharField(max_length=50)
    organism =  models.CharField(max_length=50)
    genes = models.ManyToManyField(Gene, related_name="pathways")
