from factory import DjangoModelFactory, Faker, Sequence, SubFactory
from toxsign.ontologies.models import *

class OntologyFactory(DjangoModelFactory):
    # No setting up as_parent and as_ancestor. Can't get it working with factoryboy
    name = Faker("name")
    synonyms = Faker("text")
    onto_id = Sequence(lambda n: "GO%03d" % n)


class BiologicalFactory(OntologyFactory):
    class Meta:
        model = Biological

class CellLineFactory(OntologyFactory):
    class Meta:
        model = CellLine

class CellFactory(OntologyFactory):
    class Meta:
        model = Cell

class ChemicalFactory(OntologyFactory):
    class Meta:
        model = Chemical

class DiseaseFactory(OntologyFactory):
    class Meta:
        model = Disease

class ExperimentFactory(OntologyFactory):
    class Meta:
        model = Experiment

class SpeciesFactory(OntologyFactory):
    class Meta:
        model = Species

class TissueFactory(OntologyFactory):
    class Meta:
        model = Tissue
