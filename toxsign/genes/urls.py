from django.urls import path, re_path
from .views import *

app_name = 'genes'
# Define urls here
urlpatterns = [
    re_path(r'^gene-autocomplete/$', GeneAutocomplete.as_view(), name='gene-autocomplete'),
    path('gene/<int:gene_id>', get_gene, name="get_gene")
]
