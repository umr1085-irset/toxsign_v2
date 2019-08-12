from django.urls import re_path, path
from toxsign.ontologies.views import *

app_name = "ontologies"
urlpatterns = [
    re_path(r'^biological-autocomplete/$', BiologicalAutocomplete.as_view(), name='biological-autocomplete'),
    re_path(r'^cellline-autocomplete/$', CellLineAutocomplete.as_view(), name='cellline-autocomplete'),
    re_path(r'^cell-autocomplete/$', CellAutocomplete.as_view(), name='cell-autocomplete'),
    re_path(r'^chemical-autocomplete/$', ChemicalAutocomplete.as_view(), name='chemical-autocomplete'),
    re_path(r'^disease-autocomplete/$', DiseaseAutocomplete.as_view(), name='disease-autocomplete'),
    re_path(r'^experiment-autocomplete/$', ExperimentAutocomplete.as_view(), name='experiment-autocomplete'),
    re_path(r'^species-autocomplete/$', SpeciesAutocomplete.as_view(), name='species-autocomplete'),
    re_path(r'^tissue-autocomplete/$', TissueAutocomplete.as_view(), name='tissue-autocomplete'),
    path('search', DetailView, name='search')
]
