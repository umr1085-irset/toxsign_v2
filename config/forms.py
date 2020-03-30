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
            Div(id='error_field', style='color:red; text-align:center;'),
            Div('type', style="display:none", id="id_type_wrapper"),
            Div('field', id="id_field_wrapper"),
            Div('value', style="display:none", id="id_value_wrapper"),
            Div(HTML("<button class='btn btn-primary' id='add_argument'><i class='fas fa-plus'></i></button>"), style="text-align:center;"),
        )


class MyModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.name.capitalize()

class SignatureSearchForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super(SignatureSearchForm, self).__init__(*args, **kwargs)

        self.entity_fields = ['disease', 'organism', 'chemical', 'cell', 'cell_line', 'technology', 'tissue']
        choices = (('', 'Select a field'),)

        data = {
            'disease': Disease.objects.filter(signature_used_in__isnull=False).distinct(),
            'organism': Species.objects.filter(signature_used_in__isnull=False).distinct(),
            'chemical': Chemical.objects.filter(signature_used_in__isnull=False).distinct(),
            'cell': Cell.objects.filter(signature_used_in__isnull=False).distinct(),
            'cell_line': CellLine.objects.filter(signature_used_in__isnull=False).distinct(),
            'tissue': Tissue.objects.filter(signature_used_in__isnull=False).distinct(),
            'technology': Experiment.objects.filter(signature_used_in__isnull=False).distinct(),
        }

        for field in self.entity_fields:
            if field in data and data[field]:
                choices += ((field, field.capitalize()),)
                self.fields[field] = MyModelChoiceField(queryset=data[field], required=False)

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
        )

        for field in self.entity_fields:
            if field in data and data[field]:
                 self.helper.layout.append(Div(field, style="display:none", id="id_" + field + "_ontology_wrapper"))

        self.helper.layout.append(Div(HTML("<button class='btn btn-primary' id='add_argument'><i class='fas fa-plus'></i></button>"), style="text-align:center;"))
