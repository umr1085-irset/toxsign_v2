from typing import Any, Sequence

from factory import DjangoModelFactory, Faker, post_generation
from toxsign.groups.models import Group

class GroupFactory(DjangoModelFactory):

    name = Faker("name")

    class Meta:
        model = Group
