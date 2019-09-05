from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout
from crispy_forms.bootstrap import FormActions

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from toxsign.superprojects.models import Superproject

class SuperprojectCreateForm(forms.ModelForm):

    class Meta:
        model = Superproject
        fields = ["name", "description"]

    def __init__(self, *args, **kwargs):
        super(SuperprojectCreateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('save', 'Save'))

class SuperprojectEditForm(SuperprojectCreateForm):
    pass
