import pytest

from toxsign.studies.tests.factories import StudyFactory

pytestmark = pytest.mark.django_db

def test_project_model():

    study = StudyFactory.create(name='my_new_study')
    assert project.name == 'my_new_study'
