from django import forms

from dal import autocomplete
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, HTML, Div

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from toxsign.projects.models import Project
from toxsign.ontologies.models import *

# Should be able to merge them in one form.. unless we need specific fields
class ProjectSearchForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(ProjectSearchForm, self).__init__(*args, **kwargs)

        self.entity_fields = ['name','tsx_id','description']
        choices = (('', 'Select a field'),)

        for field in self.entity_fields:
            choices += ((field, field.capitalize()),)

        self.fields["type"] = forms.ChoiceField(choices=(("AND","AND"),("OR","OR"),))
        self.fields["field"] = forms.ChoiceField(choices=choices)
        self.fields["value"] = forms.CharField()
        self.helper = FormHelper(self)
        self.helper.form_method = 'POST'
        self.helper.form_id = "advanced_search_form"
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        # Wrapping in div to hide the label and the field
        self.helper.layout = Layout(
            Div(id='error_field', style='color:red'),
            Div('type', style="display:none; text-align:center;", id="id_type_wrapper"),
            Div('field', id="id_field_wrapper"),
            Div('value', style="display:none", id="id_value_wrapper"),
            Div(HTML("<button class='btn btn-primary' id='add_argument'><i class='fas fa-plus'></i></button>"), style="text-align:center;"),
        )


class StudySearchForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(StudySearchForm, self).__init__(*args, **kwargs)

        self.entity_fields = ['name', 'tsx_id']
        choices = (('', 'Select a field'),)

        for field in self.entity_fields:
            choices += ((field, field.capitalize()),)

        self.fields["type"] = forms.ChoiceField(choices=(("AND","AND"),("OR","OR"),))
        self.fields["field"] = forms.ChoiceField(choices=choices)
        self.fields["value"] = forms.CharField()
        self.helper = FormHelper(self)
        self.helper.form_method = 'POST'
        self.helper.form_id = "advanced_search_form"
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        # Wrapping in div to hide the label and the field
        self.helper.layout = Layout(
            Div(id='error_field', style='color:red; text-align:center;'),
            Div('type', style="display:none", id="id_type_wrapper"),
            Div('field', id="id_field_wrapper"),
            Div('value', style="display:none", id="id_value_wrapper"),
            Div(HTML("<button class='btn btn-primary' id='add_argument'><i class='fas fa-plus'></i></button>"), style="text-align:center;"),
        )


class SignatureSearchForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(SignatureSearchForm, self).__init__(*args, **kwargs)

        self.entity_fields = ['name', 'tsx_id', 'disease']
        choices = (('', 'Select a field'),)

        for field in self.entity_fields:
            choices += ((field, field.capitalize()),)

        self.fields["type"] = forms.ChoiceField(choices=(("AND","AND"),("OR","OR"),))
        self.fields["field"] = forms.ChoiceField(choices=choices)
        self.fields["value"] = forms.CharField()
        self.fields["disease"] = forms.ModelChoiceField(
                                    queryset=Disease.objects.all(),
                                    required=False,
                                    widget=autocomplete.ModelSelect2(url='/ontologies/disease-autocomplete', attrs={'data-minimum-input-length': 3})
                                )
        self.fields["onto_type"] = forms.ChoiceField(choices=(("SOLO","Term only"),("CHILDREN","Include children"),))

        self.helper = FormHelper(self)
        self.helper.form_method = 'POST'
        self.helper.form_id = "advanced_search_form"
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        # Wrapping in div to hide the label and the field
        self.helper.layout = Layout(
            Div(id='error_field', style='color:red; text-align:center;'),
            Div('type', style="display:none", id="id_type_wrapper"),
            Div('field', id="id_field_wrapper"),
            Div('value', style="display:none", id="id_value_wrapper"),
            Div('disease', style="display:none", id="id_disease_ontology_wrapper"),
            Div('onto_type', style="display:none", id="id_onto_type_wrapper"),
            Div(HTML("<button class='btn btn-primary' id='add_argument'><i class='fas fa-plus'></i></button>"), style="text-align:center;"),
        )
