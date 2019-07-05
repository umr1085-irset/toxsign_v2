from factory import DjangoModelFactory, Faker, SubFactory
from toxsign.projects.models import Project
from toxsign.users.tests.factories import UserFactory

class ProjectFactory(DjangoModelFactory):

    name = Faker("name")
    created_by = SubFactory(UserFactory)
    status = "PRIVATE"
    description = Faker("text")

    class Meta:
        model = Project
