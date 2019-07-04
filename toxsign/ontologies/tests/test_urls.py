import pytest

from django.urls import reverse, resolve
from django.test import Client

from toxsign.ontologies.tests.factories import BiologicalFactory

pytestmark = pytest.mark.django_db

def test_list():
    assert reverse("ontologies:index") == ""
    assert resolve("").view_name == "ontologies:index"

def test_details():
    ontology = BiologicalFactory.create(as_parent=None, as_ancestor=None)
    assert (
        reverse("ontologies:detail", kwargs={"pk": ontology.id})
        == f"{ontology.id}/"
    )
    assert resolve(f"{ontology.id}/").view_name == "ontologies:detail"
