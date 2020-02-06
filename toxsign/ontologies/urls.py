from django.urls import re_path, path
from toxsign.ontologies.views import *

app_name = "ontologies"
urlpatterns = [
    re_path(r'^cellline-autocomplete/$', CellLineAutocomplete.as_view(), name='cellline-autocomplete'),
    re_path(r'^cell-autocomplete/$', CellAutocomplete.as_view(), name='cell-autocomplete'),
    re_path(r'^chemical-autocomplete/$', ChemicalAutocomplete.as_view(), name='chemical-autocomplete'),
    re_path(r'^disease-autocomplete/$', DiseaseAutocomplete.as_view(), name='disease-autocomplete'),
    re_path(r'^experiment-autocomplete/$', ExperimentAutocomplete.as_view(), name='experiment-autocomplete'),
    re_path(r'^species-autocomplete/$', SpeciesAutocomplete.as_view(), name='species-autocomplete'),
    re_path(r'^tissue-autocomplete/$', TissueAutocomplete.as_view(), name='tissue-autocomplete'),
    re_path(r'^cellline-restricted-autocomplete/$', CellLineRestrictedAutocomplete.as_view(), name='cellline-restricted-autocomplete'),
    re_path(r'^cell-restricted-autocomplete/$', CellRestrictedAutocomplete.as_view(), name='cell-restricted-autocomplete'),
    re_path(r'^chemical-restricted-autocomplete/$', ChemicalRestrictedAutocomplete.as_view(), name='chemical-restricted-autocomplete'),
    re_path(r'^disease-restricted-autocomplete/$', DiseaseRestrictedAutocomplete.as_view(), name='disease-restricted-autocomplete'),
    re_path(r'^experiment-restricted-autocomplete/$', ExperimentRestrictedAutocomplete.as_view(), name='experiment-restricted-autocomplete'),
    re_path(r'^species-restricted-autocomplete/$', SpeciesRestrictedAutocomplete.as_view(), name='species-restricted-autocomplete'),
    re_path(r'^tissue-restricted-autocomplete/$', TissueRestrictedAutocomplete.as_view(), name='tissue-restricted-autocomplete'),
    path('search', DetailView, name='search')
]
