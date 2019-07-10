from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout
from crispy_forms.bootstrap import FormActions

from toxsign.projects.models import Project

class ProjectCreateForm(forms.ModelForm):

    class Meta:
        model = Project
        fields = ["name", "status", "description"]

    def __init__(self, *args, **kwargs):
        super(ProjectCreateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('save', 'Save'))
#        self.helper.layout = Layout(FormActions(Submit('BlahBlah', 'BlahBlah', css_class='btn-primary')))
