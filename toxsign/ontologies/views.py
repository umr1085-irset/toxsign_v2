from dal import autocomplete
from django.db.models import Q
from toxsign.ontologies.models import *
import toxsign.ontologies.forms as ontologies_forms
from django.shortcuts import render
import toxsign.ontologies.models as models
from django.http import JsonResponse
from django.apps import apps
from toxsign.ontologies.forms import BiologicalForm

class OntologyAutocomplete(autocomplete.Select2QuerySetView):

    def __init__(self, model):
        self.model = model

    def get_queryset(self):
        if not self.request.user.is_authenticated:
                    return self.model.objects.none()
        qs = self.model.objects.all()
        if self.q:
            qs = qs.filter(Q(name__istartswith=self.q))
        return qs

class BiologicalAutocomplete(OntologyAutocomplete):
    def __init__(self):
        super(BiologicalAutocomplete, self).__init__(Biological)

class CellLineAutocomplete(OntologyAutocomplete):
    def __init__(self):
        super(CellLineAutocomplete, self).__init__(CellLine)

class CellAutocomplete(OntologyAutocomplete):
     def __init__(self):
         super(CellAutocomplete, self).__init__(Cell)

class ChemicalAutocomplete(OntologyAutocomplete):
    def __init__(self):
        super(ChemicalAutocomplete, self).__init__(Chemical)

class DiseaseAutocomplete(OntologyAutocomplete):
    def __init__(self):
        super(DiseaseAutocomplete, self).__init__(Disease)

class ExperimentAutocomplete(OntologyAutocomplete):
    def __init__(self):
        super(ExperimentAutocomplete, self).__init__(Experiment)

class SpeciesAutocomplete(OntologyAutocomplete):
    def __init__(self):
        super(SpeciesAutocomplete, self).__init__(Species)

class TissueAutocomplete(OntologyAutocomplete):
    def __init__(self):
        super(TissueAutocomplete, self).__init__(Tissue)

def DetailView(request):

    if request.method == 'POST':
        data = request.POST
        dict = {'html': ""}
        for field, value in data.items():
            if not field == 'csrfmiddlewaretoken':
                if value:
                    model = getattr(models, field)
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
