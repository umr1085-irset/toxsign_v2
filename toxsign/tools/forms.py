from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator

class python_printForm(forms.Form):
    job_name = forms.CharField(label='Job_name', max_length=100)
    characters = forms.CharField(label='Chain of charaters', max_length=200)

class module_006_Form(forms.Form):
    job_name = forms.CharField(label='Job_name', max_length=100)
    characters = forms.CharField(label='Chain of charaters', max_length=200)

class module_007_Form(forms.Form):
    job_name = forms.CharField(label='Job_name', max_length=100)
    characters = forms.CharField(label='Chain of charaters', max_length=200)
    