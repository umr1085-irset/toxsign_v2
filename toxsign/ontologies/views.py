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

class BiologicalAutocomplete(autocomplete.Select2QuerySetView):

    def get_queryset(self):
        if not self.request.user.is_authenticated:
                    return Biological.objects.none()

        qs = BiologicalDocument.search()
        if self.q:
            qs = qs.query("prefix", name=self.q)
        return qs

    def get_result_value(self, result):
        return result.id

    def get_result_label(self, result):
        return result.name

class CellLineAutocomplete(autocomplete.Select2QuerySetView):

    def get_queryset(self):
        if not self.request.user.is_authenticated:
                    return CellLine.objects.none()

        qs = CellLineDocument.search()
        if self.q:
            qs = qs.query("prefix", name=self.q)
        return qs

    def get_result_value(self, result):
        return result.id

    def get_result_label(self, result):
        return result.name

class CellAutocomplete(autocomplete.Select2QuerySetView):

    def get_queryset(self):
        if not self.request.user.is_authenticated:
                    return Cell.objects.none()

        qs = CellDocument.search()
        if self.q:
            qs = qs.query("prefix", name=self.q)
        return qs

    def get_result_value(self, result):
        return result.id

    def get_result_label(self, result):
        return result.name

class ChemicalAutocomplete(autocomplete.Select2QuerySetView):

    def get_queryset(self):
        if not self.request.user.is_authenticated:
                    return Disease.objects.none()

        qs = ChemicalDocument.search()
        if self.q:
            qs = qs.query("prefix", name=self.q)
        return qs

    def get_result_value(self, result):
        return result.id

    def get_result_label(self, result):
        return result.name

class DiseaseAutocomplete(autocomplete.Select2QuerySetView):

    def get_queryset(self):
        if not self.request.user.is_authenticated:
                    return Disease.objects.none()

        qs = DiseaseDocument.search()
        if self.q:
            qs = qs.query("prefix", name=self.q)
        return qs

    def get_result_value(self, result):
        return result.id

    def get_result_label(self, result):
        return result.name

class ExperimentAutocomplete(autocomplete.Select2QuerySetView):

    def get_queryset(self):
        if not self.request.user.is_authenticated:
                    return Experiment.objects.none()

        qs = ExperimentDocument.search()
        if self.q:
            qs = qs.query("prefix", name=self.q)
        return qs

    def get_result_value(self, result):
        return result.id

    def get_result_label(self, result):
        return result.name

class SpeciesAutocomplete(autocomplete.Select2QuerySetView):

    def get_queryset(self):
        if not self.request.user.is_authenticated:
                    return Species.objects.none()

        qs = SpeciesDocument.search()
        if self.q:
            qs = qs.query("prefix", name=self.q)
        return qs

    def get_result_value(self, result):
        return result.id

    def get_result_label(self, result):
        return result.name

class TissueAutocomplete(autocomplete.Select2QuerySetView):

    def get_queryset(self):
        if not self.request.user.is_authenticated:
                    return Tissue.objects.none()

        qs = TissueDocument.search()
        if self.q:
            qs = qs.query("prefix", name=self.q)
        return qs

    def get_result_value(self, result):
        return result.id

    def get_result_label(self, result):
        return result.name

def DetailView(request):

    if request.method == 'POST':
        data = request.POST
        dict = {'html': ""}
        for field, value in data.items():
            if not field == 'csrfmiddlewaretoken':
                if value:
                    model = getattr(ontologymodels, field)
                    object = model.objects.get(id=value)
                    dict['html'] = "<p><b>Pathology name : </b>{}</p>".format(object.name)
                    dict['html'] +="<p><b>Ontology ID : </b>{}</p>".format(object.onto_id)
                    dict['html'] +="<p><b>Synonyms : </b>{}</p>".format(object.synonyms.replace('|', ','))
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
