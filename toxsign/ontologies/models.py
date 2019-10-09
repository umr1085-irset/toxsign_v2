from django.contrib.auth.models import AbstractUser
from django.db.models import CharField
from django.urls import reverse
from django.db import models
from django.contrib.auth.models import  User, Group
from django.conf import settings



class Biological(models.Model):
    name = models.CharField(max_length=200)
    synonyms =  models.TextField("Synonyms", blank=True, default="")
    onto_id = models.CharField(max_length=200)
    as_children =  models.TextField("Children", blank=True, default="") #all parents

    def __str__(self):
        return self.name

class CellLine(models.Model):
    name = models.CharField(max_length=200)
    synonyms =  models.TextField("Synonyms", blank=True, default="")
    onto_id = models.CharField(max_length=200)
    as_children =  models.TextField("Children", blank=True, default="") #all parents

    def __str__(self):
        return self.name

class Cell(models.Model):
    name = models.CharField(max_length=200)
    synonyms =  models.TextField("Synonyms", blank=True, default="")
    onto_id = models.CharField(max_length=200)
    as_children =  models.TextField("Children", blank=True, default="") #all parents

    def __str__(self):
        return self.name

class Chemical(models.Model):
    name = models.CharField(max_length=200)
    synonyms =  models.TextField("Synonyms", blank=True, default="")
    onto_id = models.CharField(max_length=200)
    as_children =  models.TextField("Children", blank=True, default="") #all parents

    def __str__(self):
        return self.name

class Disease(models.Model):
    name = models.CharField(max_length=200)
    synonyms =  models.TextField("Synonyms", blank=True, default="")
    onto_id = models.CharField(max_length=200)
    as_children =  models.TextField("Children", blank=True, default="") #all parents

    def __str__(self):
        return self.name

class Experiment(models.Model):
    name = models.CharField(max_length=200)
    synonyms =  models.TextField("Synonyms", blank=True, default="")
    onto_id = models.CharField(max_length=200)
    as_children =  models.TextField("Children", blank=True, default="") #all parents

    def __str__(self):
        return self.name

class Species(models.Model):
    name = models.CharField(max_length=200)
    synonyms =  models.TextField("Synonyms", blank=True, default="")
    onto_id = models.CharField(max_length=200)
    as_children =  models.TextField("Children", blank=True, default="") #all parents

    def __str__(self):
        return self.name

class Tissue(models.Model):
    name = models.CharField(max_length=200)
    synonyms =  models.TextField("Synonyms", blank=True, default="")
    onto_id = models.CharField(max_length=200)
    as_children =  models.TextField("Children", blank=True, default="") #all parents

    def __str__(self):
        return self.name
