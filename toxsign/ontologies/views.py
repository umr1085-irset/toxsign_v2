from dal import autocomplete
from django.db.models import Q
from toxsign.ontologies.models import *

class OntologyAutocomplete(autocomplete.Select2QuerySetView):

    def __init__(self, model):
        self.model = model

    def get_queryset(self):
        if not self.request.user.is_authenticated():
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
