from dal import autocomplete
from django.db.models import Q
from toxsign.ontologies.models import *
import toxsign.ontologies.forms as ontologies_forms
from django.shortcuts import render
from django.http import JsonResponse
from django.apps import apps
from toxsign.ontologies.forms import BiologicalForm
from toxsign.ontologies.documents import *
import toxsign.ontologies.models as ontologymodels

class OntologyAutocomplete(autocomplete.Select2QuerySetView):

    def get_result_value(self, result):
        return result.id

    def get_result_label(self, result):
        return result.name

class BiologicalAutocomplete(OntologyAutocomplete):

    def get_queryset(self):
        return(get_results(self.q, Biological, BiologicalDocument))

class CellLineAutocomplete(OntologyAutocomplete):

    def get_queryset(self):
        return(get_results(self.q, CellLine, CellLineDocument))

class CellAutocomplete(OntologyAutocomplete):

    def get_queryset(self):
        return(get_results(self.q, Cell, CellDocument))

class ChemicalAutocomplete(OntologyAutocomplete):

    def get_queryset(self):
        return(get_results(self.q, Chemical, ChemicalDocument))

class DiseaseAutocomplete(OntologyAutocomplete):

    def get_queryset(self):
        return(get_results(self.q, Disease, DiseaseDocument))

class ExperimentAutocomplete(OntologyAutocomplete):

    def get_queryset(self):
        return(get_results(self.q, Experiment, ExperimentDocument))

class SpeciesAutocomplete(OntologyAutocomplete):

    def get_queryset(self):
        return(get_results(self.q, Species, SpeciesDocument))

class TissueAutocomplete(OntologyAutocomplete):

    def get_queryset(self):
        return(get_results(self.q, Tissue, TissueDocument))

def get_results(query, Model, Document):
    try:
        # No need to restrict to authenticated
        qs = Document.search()
        if query:
            qs = qs.query("prefix", name=query)
        return qs
        # Fall back to DB search if failure for any reason
    except Exception as e:
        qs = Model.objects.all()
        if query:
            qs = qs.filter(Q(name__istartswith=query))
        return qs

def DetailView(request):

    if request.method == 'POST':
        data = request.POST
        dict = {'html': ""}
        for field, value in data.items():
            if not field == 'csrfmiddlewaretoken':
                if value:
                    model = getattr(ontologymodels, field)
                    object = model.objects.get(id=value)
                    dict['html'] = "<p><b>Ontology name : </b>{}</p>".format(object.name)
                    dict['html'] +="<p><b>Ontology ID : </b>{}</p>".format(object.onto_id)
                    dict['html'] +="<p><b>Synonyms : </b>{}</p>".format(object.synonyms)
        return JsonResponse(dict)

    else:
        forms = []
        app_models = apps.get_app_config('ontologies').get_models()
        for model in app_models:
            name = model.__name__
            id = name + "-id"
            form = getattr(ontologies_forms, name + "Form")
            forms.append({'id': id, 'form': form()})

        return render(request, 'ontologies/details.html', {'forms': forms})
