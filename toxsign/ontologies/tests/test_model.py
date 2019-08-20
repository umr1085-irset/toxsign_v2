import pytest

from toxsign.ontologies.tests.factories import DiseaseFactory
from toxsign.ontologies.models import Disease

pytestmark = pytest.mark.django_db

def test_project_model():
    ontology = DiseaseFactory.build(name='my_ont')
    assert ontology.name == 'my_ont'

def test_data_load():
    ontologies = Disease.objects.all()
    assert len(ontologies) == 2497
