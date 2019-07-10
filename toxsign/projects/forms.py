from django import forms
from toxsign.projects.models import Project

class ProjectCreateForm(forms.ModelForm):

    class Meta:
        model = Project
        fields = ["name", "status", "description"]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(BookCreateForm, self).__init__(*args, **kwargs)
