from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, HTML

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from toxsign.projects.models import Project

class ProjectSearchForm(forms.Form):

    def __init__(self, *args, **kwargs):
        self.entity_fields = kwargs.pop('fields')
        super(ProjectSearchForm, self).__init__(*args, **kwargs)

        choices = (('', '----'),)

        for field in self.entity_fields:
            choices += ((field, field),)

        self.fields["type"] = forms.ChoiceField(choices=(("AND","AND"),("OR","OR"),))
        self.fields['type'].widget.attrs.update({'style' : 'display:none;'})
        self.fields["field"] = forms.ChoiceField(choices=choices)
        self.fields["value"] = forms.CharField()
        self.helper = FormHelper(self)
        self.helper.form_method = 'POST'
        self.helper.field_template = 'bootstrap3/layout/inline_field.html'
        self.helper.form_id = "advanced_search_form"
        self.helper.form_class = 'form-inline'
        self.helper.layout = Layout(
            'type',
            'field',
            'value',
            HTML("<button class='btn btn-primary' id='add_argument'><i class='fas fa-plus'></i></button>"),
        )
