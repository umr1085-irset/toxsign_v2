from django import forms
from toxsign.projects.models import Project

class ProjectForm(forms.ModelForm):

    class Meta:
        model = Project
        fields = ["name", "status", "description"]
