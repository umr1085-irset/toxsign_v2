from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout
from crispy_forms.bootstrap import FormActions
from toxsign.studies.models import Study



class StudyCreateForm(forms.ModelForm):

    class Meta:
        model = Study
        fields = ["name", "description", "experimental_design", "study_type", "results"]

    def __init__(self, *args, **kwargs):
        self.study = kwargs.pop('study', None)

        super(StudyCreateForm, self).__init__(*args, **kwargs)

        if self.study:
            self.fields['name'].initial = self.study.name
            self.fields['description'].initial = self.study.description
            self.fields['experimental_design'].initial = self.study.experimental_design
            self.fields['study_type'].initial = self.study.study_type
            self.fields['results'].initial = self.study.results

        self.helper = FormHelper(self)
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('save', 'Save'))


class StudyEditForm(StudyCreateForm):

    def __init__(self, *args, **kwargs):
        super(StudyCreateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('save', 'Save'))

