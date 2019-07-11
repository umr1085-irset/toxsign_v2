from factory import DjangoModelFactory, Faker, SubFactory
from toxsign.signatures.models import Study
from toxsign.projects.tests.factories import ProjectFactory
from toxsign.users.tests.factories import UserFactory

class StudyFactory(DjangoModelFactory):

    name = Faker("name")
    tsx_id = Faker("first_name")
    created_by = SubFactory(UserFactory)
    description = Faker("text")
    experimental_design = Faker("text")
    study_type = 'INTERVENTIONAL'
    results = Faker("text")
    project = SubFactory(ProjectFactory)

    class Meta:
        model = Study
