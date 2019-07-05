import pytest

from toxsign.studies.tests.factories import StudyFactory

pytestmark = pytest.mark.django_db

def test_study_model():

    study = StudyFactory.create(name='my_new_study')
    assert study.name == 'my_new_study'
