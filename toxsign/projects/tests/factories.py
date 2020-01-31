from factory import DjangoModelFactory, Faker, SubFactory, post_generation
from toxsign.projects.models import Project
from toxsign.users.tests.factories import UserFactory

class ProjectFactory(DjangoModelFactory):

    name = Faker("name")
    created_by = SubFactory(UserFactory)
    status = "PRIVATE"
    description = Faker("text")

    class Meta:
        model = Project

    @post_generation
    def read_groups(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of groups were passed in, use them
            for group in extracted:
                self.read_groups.add(group)

    @post_generation
    def edit_groups(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of groups were passed in, use them
            for group in extracted:
                self.edit_groups.add(group)
