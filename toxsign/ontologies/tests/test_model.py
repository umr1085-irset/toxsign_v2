import pytest

from toxsign.ontologies.tests.factories import BiologicalFactory
from toxsign.ontologies.models import Biological

pytestmark = pytest.mark.django_db

def test_project_model():
    ontology = BiologicalFactory.create(name='my_ont')
    assert ontology.name == 'my_ont'

def test_data_load():
    ontologies = Biological.objects.all()
    assert len(ontologies) == 2497
