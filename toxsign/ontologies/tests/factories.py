from factory import DjangoModelFactory, Faker, Sequence, SubFactory
from toxsign.ontologies.models import Biological, Disease

class OntologyFactory(DjangoModelFactory):
    # No setting up as_parent and as_ancestor. Can't get it working with factoryboy
    name = Faker("name")
    synonyms = Faker("text")
    onto_id = Sequence(lambda n: "GO%03d" % n)


class BiologicalFactory(OntologyFactory):
    class Meta:
        model = Biological

class DiseaseFactory(OntologyFactory):
    class Meta:
        model = Disease
