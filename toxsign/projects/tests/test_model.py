import pytest

from toxsign.projects.tests.factories import ProjectFactory

pytestmark = pytest.mark.django_db

def test_project_model():

#    project = ProjectFactory(name='my_new_project')
    project = ProjectFactory.create(name='my_new_project')
    assert project.name == 'my_new_project'
    assert project.tsx_id == 'TSP' + str(project.id)
