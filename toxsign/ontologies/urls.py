from django.urls import re_path
from toxsign.ontologies.views import DiseaseAutocomplete

app_name = "ontologies"
urlpatterns = [
    re_path(r'^disease-autocomplete/$', DiseaseAutocomplete.as_view(), name='disease-autocomplete'),
]
