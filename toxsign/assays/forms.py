from django import forms
from dal import autocomplete
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout
from crispy_forms.bootstrap import FormActions
from toxsign.assays.models import Assay, Factor
from toxsign.ontologies.models import Cell, CellLine, Chemical, Species, Tissue


class AssayCreateForm(forms.ModelForm):

    cell_line = forms.ModelChoiceField(
                    queryset=CellLine.objects.all(),
                    widget=autocomplete.ModelSelect2(url='/ontologies/cellline-autocomplete')
                    )
    cell = forms.ModelChoiceField(
                queryset=Cell.objects.all(),
                widget=autocomplete.ModelSelect2(url='/ontologies/cell-autocomplete')
                )
    organism = forms.ModelChoiceField(
                    queryset=Species.objects.all(),
                    widget=autocomplete.ModelSelect2(url='/ontologies/species-autocomplete')
                    )
    tissue = forms.ModelChoiceField(
                queryset=Tissue.objects.all(),
                widget=autocomplete.ModelSelect2(url='/ontologies/tissue-autocomplete')
                )

    class Meta:
        model = Assay
        exclude = ("tsx_id", "created_at", "created_by", "updated_at", "study", )

    def __init__(self, *args, **kwargs):
        super(AssayCreateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('save', 'Save'))

class FactorCreateForm(forms.ModelForm):

    chemical = forms.ModelChoiceField(
                    queryset=Chemical.objects.all(),
                    widget=autocomplete.ModelSelect2(url='/ontologies/chemical-autocomplete')
                    )

    class Meta:
        model = Factor
        exclude = ("tsx_id", "created_at", "created_by", "updated_at", "assay", )

    def __init__(self, *args, **kwargs):
        super(FactorCreateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('save', 'Save'))
