import pytest

from django.urls import reverse, resolve
from django.test import Client

from toxsign.ontologies.tests.factories import BiologicalFactory

pytestmark = pytest.mark.django_db

class TestProjectListView:
    # Use this to check it the ontologies were populated at launch
    # No need to create a new one
    def test_list_views(self, client):
        response = client.get(reverse('ontologies:index'))
        projects = response.context['onto_list']
        assert len(projects) == 2497

class TestProjectDetailView:

    def test_details_view_anonymous(self, client):
        ontology = BiologicalFactory.create(as_parent=None, as_ancestor=None)
        response = client.get(reverse("projects:detail", kwargs={"prjid": project.tsx_id}))
        response_project = projects = response.context['project']
        assert project == response_project

    def test_details_view_user(self, client):
        ontology = BiologicalFactory.create(as_parent=None, as_ancestor=None)
        response = client.get(reverse("projects:detail", kwargs={"prjid": project.tsx_id}))
        response_project = projects = response.context['project']
        assert project == response_project
