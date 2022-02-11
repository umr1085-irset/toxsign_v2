from django import forms
from dal import autocomplete
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout
from crispy_forms.bootstrap import FormActions

from toxsign.assays.models import Assay
from toxsign.signatures.models import Signature
from toxsign.ontologies.models import *


class SignatureCreateForm(forms.ModelForm):

    cell_line = forms.ModelChoiceField(
                queryset=CellLine.objects.all(),
                required=False,
                widget=autocomplete.ModelSelect2(url='/ontologies/cellline-autocomplete', attrs={'data-minimum-input-length': 3})
              )
    cell = forms.ModelChoiceField(
                queryset=Cell.objects.all(),
                required=False,
                widget=autocomplete.ModelSelect2(url='/ontologies/cell-autocomplete', attrs={'data-minimum-input-length': 3})
              )
    chemical = forms.ModelChoiceField(
                queryset=Chemical.objects.all(),
                required=False,
                widget=autocomplete.ModelSelect2(url='/ontologies/chemical-autocomplete', attrs={'data-minimum-input-length': 3})
              )
    disease = forms.ModelChoiceField(
                queryset=Disease.objects.all(),
                required=False,
                widget=autocomplete.ModelSelect2(url='/ontologies/disease-autocomplete', attrs={'data-minimum-input-length': 3})
              )
    technology = forms.ModelChoiceField(
                queryset=Experiment.objects.all(),
                required=False,
                widget=autocomplete.ModelSelect2(url='/ontologies/experiment-autocomplete', attrs={'data-minimum-input-length': 3})
              )
    organism = forms.ModelChoiceField(
                queryset=Species.objects.all(),
                required=False,
                widget=autocomplete.ModelSelect2(url='/ontologies/species-autocomplete', attrs={'data-minimum-input-length': 3})
              )
    tissue = forms.ModelChoiceField(
                queryset=Tissue.objects.all(),
                required=False,
                widget=autocomplete.ModelSelect2(url='/ontologies/tissue-autocomplete', attrs={'data-minimum-input-length': 3})
              )

    class Meta:
        model = Signature
        exclude = ("tsx_id", "created_at", "created_by", "updated_at", "expression_values", "expression_values_file", "up_gene_number", "down_gene_number", "interrogated_gene_number")

    def __init__(self, *args, **kwargs):

        self.factors = kwargs.pop('factor')
        self.sig = kwargs.pop('sig', None)

        super(SignatureCreateForm, self).__init__(*args, **kwargs)

        self.fields['factor'].queryset = self.factors
        if self.factors.count() == 1:
            self.fields['factor'].initial = self.factors.first()

        list = []
        if self.sig:
            for key, value in self.fields.items():
                if getattr(self.sig, key):
                    value.initial = getattr(self.sig, key)

        self.helper = FormHelper(self)
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('save', 'Save'))

class SignatureEditForm(SignatureCreateForm):

    def __init__(self, *args, **kwargs):
        self.factors = kwargs.pop('factor')
        super(SignatureCreateForm, self).__init__(*args, **kwargs)
        self.fields['factor'].queryset = self.factors
        self.helper = FormHelper(self)
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('save', 'Save'))
