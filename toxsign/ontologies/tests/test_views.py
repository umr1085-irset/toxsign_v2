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

#class TestProjectDetailView:
# TBA when the view for this is actually functionnal
