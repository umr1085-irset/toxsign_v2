from django import forms

from django.forms.models import inlineformset_factory

from dal import autocomplete
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout
from crispy_forms.bootstrap import FormActions
from toxsign.assays.models import Assay, Factor, ChemicalsubFactor
from toxsign.ontologies.models import Cell, CellLine, Chemical, Species, Tissue

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class AssayCreateForm(forms.ModelForm):

    cell_line = forms.ModelChoiceField(
                    queryset=CellLine.objects.all(),
                    required=False,
                    widget=autocomplete.ModelSelect2(url='/ontologies/cellline-autocomplete')
                    )
    cell = forms.ModelChoiceField(
                queryset=Cell.objects.all(),
                required=False,
                widget=autocomplete.ModelSelect2(url='/ontologies/cell-autocomplete')
                )
    organism = forms.ModelChoiceField(
                    queryset=Species.objects.all(),
                    required=False,
                    widget=autocomplete.ModelSelect2(url='/ontologies/species-autocomplete')
                    )
    tissue = forms.ModelChoiceField(
                queryset=Tissue.objects.all(),
                required=False,
                widget=autocomplete.ModelSelect2(url='/ontologies/tissue-autocomplete')
                )

    class Meta:
        model = Assay
        exclude = ("tsx_id", "created_at", "created_by", "updated_at", "project")

    def __init__(self, *args, **kwargs):
        self.assay = kwargs.pop('assay', None)

        super(AssayCreateForm, self).__init__(*args, **kwargs)

        if self.assay:
            self.fields['name'].initial = self.assay.name
            self.fields['additional_info'].initial = self.assay.additional_info
            self.fields['experimental_design'].initial = self.assay.experimental_design
            self.fields['dev_stage'].initial = self.assay.dev_stage
            self.fields['generation'].initial = self.assay.generation
            self.fields['sex_type'].initial = self.assay.sex_type
            self.fields['exp_type'].initial = self.assay.exp_type
            self.fields['project'].initial = self.assay.project
            self.fields['organism'].initial = self.assay.organism
            self.fields['tissue'].initial = self.assay.tissue
            self.fields['cell'].initial = self.assay.cell
            self.fields['cell_line'].initial = self.assay.cell_line

        self.helper = FormHelper(self)
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('save', 'Save'))


class AssayEditForm(AssayCreateForm):

    def __init__(self, *args, **kwargs):
        super(AssayCreateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('save', 'Save'))


class FactorCreateForm(forms.ModelForm):

    class Meta:
        model = Factor
        exclude = ("tsx_id", "created_at", "created_by", "updated_at", )

    def __init__(self, *args, **kwargs):
        self.assays = kwargs.pop('assay')
        self.factor = kwargs.pop('factor', None)

        super(FactorCreateForm, self).__init__(*args, **kwargs)

        self.fields['assay'].queryset = self.assays
        if self.assays.count() == 1:
            self.fields['assay'].initial = self.assays.first()

        if self.factor:
            self.fields['name'].initial = self.factor.name
            self.fields['assay'].initial = self.factor.assay

        self.helper = FormHelper(self)
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('save', 'Save'))

class FactorEditForm(FactorCreateForm):

    def __init__(self, *args, **kwargs):
        self.assays = kwargs.pop('assay')
        super(FactorCreateForm, self).__init__(*args, **kwargs)
        self.fields['assay'].queryset = self.assays
        self.helper = FormHelper(self)
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('save', 'Save'))

class ChemicalsubFactorCreateForm(forms.ModelForm):

    chemical = forms.ModelChoiceField(
                    queryset=Chemical.objects.all(),
                    required=False,
                    widget=autocomplete.ModelSelect2(url='/ontologies/chemical-autocomplete')
                    )

    class Meta:
        model = ChemicalsubFactor
        exclude = ("created_at", "created_by", "updated_at", "factor", )

    def __init__(self, *args, **kwargs):
        super(ChemicalsubFactorCreateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('save', 'Save'))

    def is_valid(self):
        valid = super(ChemicalsubFactorCreateForm, self).is_valid()

        if not valid:
            return valid

        if not self.cleaned_data['chemical'] and not self.cleaned_data['chemical_slug']:
            self.add_error("chemical", ValidationError(_('Please select either a chemical or a chemical slug'), code='invalid'))
            return False

        return True





class ChemicalsubFactorEditForm(ChemicalsubFactorCreateForm):

    def __init__(self, *args, **kwargs):
        super(ChemicalsubFactorCreateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('save', 'Save'))
