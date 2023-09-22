from django import forms

from dal import autocomplete
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, HTML, Div

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from toxsign.projects.models import Project
from toxsign.ontologies.models import *
from toxsign.signatures.models import Signature
from toxsign.assays.models import ChemicalsubFactor

# Should be able to merge them in one form.. unless we need specific fields


def get_model_data(ontology_model, related_field_name, entity_model=None, field_name=None, field_slug_name=None):
    data = {}

    for ontology in ontology_model.objects.filter(**{related_field_name + "__isnull":False}).distinct():
        data[ontology.name.capitalize()] = ontology.id

    if field_name and entity_model and field_slug_name:
        entities = entity_model.objects.filter(**{field_name + "__isnull":True}).exclude(**{field_slug_name + "__exact":""})
        for entity in entities:
            if getattr(entity, field_slug_name):
                data[getattr(entity, field_slug_name)] = getattr(entity, field_slug_name)

    res = []

    for key, value in data.items():
        res.append((value, key))

    res.sort(key=lambda tup: tup[1])

    return res

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
            Div(id='error_field', style='color:red; text-align:center;'),
            Div('type', style="display:none", id="id_type_wrapper"),
            Div('field', id="id_field_wrapper"),
            Div('value', style="display:none", id="id_value_wrapper"),
            Div(HTML("<button class='btn btn-primary' id='add_argument'><i class='fas fa-plus'></i></button>"), style="text-align:center;"),
        )


class MyChoiceField(forms.ChoiceField):
    def label_from_instance(self, obj):
        return obj.name.capitalize()

class SignatureSearchForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(SignatureSearchForm, self).__init__(*args, **kwargs)

        self.entity_fields = ['disease', 'organism', 'cell', 'cell_line', 'technology', 'tissue', 'chemical']
        choices = (('', 'Select a field'),)

        data = {
        #    'disease': get_model_data(Disease, "signature_used_in"),
        #    'organism': get_model_data(Species, "signature_used_in"),
        #    'technology': get_model_data(Experiment, "signature_used_in", Signature, "technology", "technology_slug"),
        #    'chemical': get_model_data(Chemical, "chemical_subfactor_used_in", ChemicalsubFactor, "chemical", "chemical_slug"),
        #    'cell': get_model_data(Cell, "signature_used_in"),
        #    'cell_line': get_model_data(CellLine, "signature_used_in", Signature, "cell_line", "cell_line_slug"),
        #    'tissue': get_model_data(Tissue, "signature_used_in")
        }

        for field in self.entity_fields:
            if field in data and data[field]:
                choices += ((field, field.capitalize()),)
                self.fields[field] = MyChoiceField(choices=[('','---------')] + data[field], required=False)

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
        )

        for field in self.entity_fields:
            if field in data and data[field]:
                 self.helper.layout.append(Div(field, css_class="entity-wrapper", id="id_" + field + "_ontology_wrapper"))

        self.helper.layout.append(Div(HTML("<button class='btn btn-primary' id='add_argument'><i class='fas fa-plus'></i></button>"), style="text-align:center;"))

