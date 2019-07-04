from factory import DjangoModelFactory, Faker, Sequence, SubFactory
from toxsign.ontologies.models import Biological

class BiologicalFactory(DjangoModelFactory):
    # No setting up as_parent and as_ancestor. Can't get it working with factoryboy
    name = Faker("name")
    synonyms = Faker("text")
    onto_id = Sequence(lambda n: "GO%03d" % n)

    class Meta:
        model = Biological
