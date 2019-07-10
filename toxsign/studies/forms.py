from django import forms
from toxsign.studies.models import Study

class StudyCreateForm(forms.ModelForm):

    class Meta:
        model = Study
        fields = ["name", "description", "experimental_design", "study_type", "results"]

    def __init__(self, *args, **kwargs):
        super(StudyCreateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('save', 'Save'))
