from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout
from crispy_forms.bootstrap import FormActions

from django.auth.models import Group

class ProjectCreateForm(forms.ModelForm):

    class Meta:
        model = Group
        fields = ["name"]
        labels = {
            "name": "Name of the group to be added"
        }

    def __init__(self, *args, **kwargs):

        super(ProjectCreateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('save', 'Save'))
