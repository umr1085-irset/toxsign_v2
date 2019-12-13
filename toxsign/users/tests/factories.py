from typing import Any, Sequence

from django.contrib.auth import get_user_model
from factory import DjangoModelFactory, Faker, post_generation
from toxsign.groups.tests.factories import GroupFactory

class UserFactory(DjangoModelFactory):

    username = Faker("user_name")
    email = Faker("email")
    name = Faker("name")

    @post_generation
    def password(self, create: bool, extracted: Sequence[Any], **kwargs):
        password = Faker(
            "password",
            length=42,
            special_chars=True,
            digits=True,
            upper_case=True,
            lower_case=True,
        ).generate(extra_kwargs={})
        self.set_password(password)

    class Meta:
        model = get_user_model()
        django_get_or_create = ["username"]

    @post_generation
    def groups(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of groups were passed in, use them
            for group in extracted:
                self.groups.add(group)
