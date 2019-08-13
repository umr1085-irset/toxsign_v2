from django import forms
from dal import autocomplete
from django.core.validators import MinValueValidator, MaxValueValidator
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout
from crispy_forms.bootstrap import FormActions
from toxsign.ontologies.models import *

class BiologicalForm(forms.Form):

    Biological = forms.ModelChoiceField(
                queryset=Biological.objects.all(),
                required=False,
                widget=autocomplete.ModelSelect2(url='/ontologies/biological-autocomplete', attrs={'data-minimum-input-length': 3, 'onchange': 'get_details("Biological-id");'})
              )
    def __init__(self, *args, **kwargs):
        super(BiologicalForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_id = "Biological-id"
        self.helper.include_media = False

class CellLineForm(forms.Form):

    CellLine = forms.ModelChoiceField(
                queryset=CellLine.objects.all(),
                required=False,
                widget=autocomplete.ModelSelect2(url='/ontologies/cellline-autocomplete', attrs={'data-minimum-input-length': 3, 'onchange': 'get_details("CellLine-id");'})
              )
    def __init__(self, *args, **kwargs):
        super(CellLineForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_id= "CellLine-id"
        self.helper.include_media = False

class CellForm(forms.Form):

    Cell = forms.ModelChoiceField(
                queryset=Cell.objects.all(),
                required=False,
                widget=autocomplete.ModelSelect2(url='/ontologies/cell-autocomplete', attrs={'data-minimum-input-length': 3, 'onchange': 'get_details("Cell-id");'})
              )
    def __init__(self, *args, **kwargs):
        super(CellForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_id = "Cell-id"
        self.helper.include_media = False

class ChemicalForm(forms.Form):
    Chemical = forms.ModelChoiceField(
                queryset=Chemical.objects.all(),
                required=False,
                widget=autocomplete.ModelSelect2(url='/ontologies/chemical-autocomplete', attrs={'data-minimum-input-length': 3, 'onchange': 'get_details("Chemical-id");'})
              )
    def __init__(self, *args, **kwargs):
        super(ChemicalForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_id = "Chemical-id"
        self.helper.include_media = False

class DiseaseForm(forms.Form):
    Disease = forms.ModelChoiceField(
                queryset=Disease.objects.all(),
                required=False,
                widget=autocomplete.ModelSelect2(url='/ontologies/disease-autocomplete', attrs={'data-minimum-input-length': 3, 'onchange': 'get_details("Disease-id");'})
              )
    def __init__(self, *args, **kwargs):
        super(DiseaseForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_id = "Disease-id"
        self.helper.include_media = False

class ExperimentForm(forms.Form):

    Experiment = forms.ModelChoiceField(
                queryset=Experiment.objects.all(),
                required=False,
                widget=autocomplete.ModelSelect2(url='/ontologies/experiment-autocomplete', attrs={'data-minimum-input-length': 3, 'onchange': 'get_details("Experiment-id");'})
              )
    def __init__(self, *args, **kwargs):
        super(ExperimentForm, self).__init__(*args, **kwargs)
        self.fields['Experiment'].label = "Technology"
        self.helper = FormHelper(self)
        self.helper.form_id = "Experiment-id"
        self.helper.include_media = False

class SpeciesForm(forms.Form):
    Species = forms.ModelChoiceField(
                queryset=Species.objects.all(),
                required=False,
                widget=autocomplete.ModelSelect2(url='/ontologies/species-autocomplete', attrs={'data-minimum-input-length': 3, 'onchange': 'get_details("Species_id");'})
              )
    def __init__(self, *args, **kwargs):
        super(SpeciesForm, self).__init__(*args, **kwargs)
        self.fields['Species'].label = "Organism"
        self.helper = FormHelper(self)
        self.helper.form_id = "Species-id"
        self.helper.include_media = False

class TissueForm(forms.Form):
    Tissue = forms.ModelChoiceField(
                queryset=Tissue.objects.all(),
                required=False,
                widget=autocomplete.ModelSelect2(url='/ontologies/tissue-autocomplete', attrs={'data-minimum-input-length': 3, 'onchange': 'get_details("Tissue-id");'})
              )
    def __init__(self, *args, **kwargs):
        super(TissueForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_id = "Tissue-id"
        self.helper.include_media = False
