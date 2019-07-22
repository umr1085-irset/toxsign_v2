from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout
from crispy_forms.bootstrap import FormActions

from toxsign.projects.models import Project

class ProjectCreateForm(forms.ModelForm):

    class Meta:
        model = Project
        fields = ["name", "status", "read_groups", "edit_groups", "description"]
        labels = {
            "status": "Visibility of the project and related entities",
            "read_groups": "Groups with viewing permissions",
            "edit_groups": "Groups with editing permissions"
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')

        super(ProjectCreateForm, self).__init__(*args, **kwargs)
        self.fields['read_groups'].help_text = "Groups allowed to view the project and all related entities. Will be ignored if the visibility is set to public"
        self.fields['edit_groups'].help_text = "Groups allowed to edit the project and all related entities. Should be a subset of the groups with view permissions"

        # TODO : Give link to group creation interface?
        groups = self.user.groups.values_list('name',flat=True)
        self.fields['read_groups'].queryset = groups
        self.fields['edit_groups'].queryset = groups

        self.helper = FormHelper(self)
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('save', 'Save'))
