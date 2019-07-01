from django import forms
from toxsign.studies.models import Study

class StudytForm(forms.ModelForm):

    class Meta:
        model = Study
        fields = ["tsx_id", "name", "status", "description"]