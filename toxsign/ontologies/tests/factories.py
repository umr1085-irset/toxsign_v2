from factory import DjangoModelFactory, Faker, SubFactory
from toxsign.ontologies.models import Biological

import random

class BiologicalFactory(DjangoModelFactory):
    name = Faker("name")
    synonym = Fake("text")
    onto_id = "GO" + str(random.randint(1,101))
    as_parent = factory.SubFactory('toxsign.ontologies.factories.BiologicalFactory')
    as_ancestor = factory.SubFactory('toxsign.ontologies.factories.BiologicalFactory')

    class Meta:
        model = Biological
