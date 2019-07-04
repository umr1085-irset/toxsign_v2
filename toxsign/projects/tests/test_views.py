import pytest

from django.urls import reverse, resolve
from django.test import Client

from toxsign.projects.tests.factories import ProjectFactory
from toxsign.users.tests.factories import UserFactory
from toxsign.projects.views import EditView


pytestmark = pytest.mark.django_db

class TestProjectListView:

    def test_list_view(self, client):
        project = ProjectFactory.create()
        client = Client()
        response = client.get(reverse('projects:index'))
        projects = response.context['project_list']
        assert len(projects) == 1
        new_project = projects[0]
        assert new_project.name == project.name

class TestProjectDetailView:

    def test_details_view(self, client):
        project = ProjectFactory.create()
        response = client.get(reverse("projects:detail", kwargs={"prjid": project.tsx_id}))
        response_project = projects = response.context['project']
        assert project == response_project

class TestProjectUpdateView:

    def test_update_anonymous(self, client):
        project = ProjectFactory.create()
        new_description = project.description + '_new'
        body = {'name': project.name, 'description': new_description}
        # This actually fails silently.. with a redirect.
        response = client.post(reverse("projects:project_edit", kwargs={"pk": project.id}), body)
        assert response.status_code == 302
        project.refresh_from_db()
        assert project.description != new_description

    def test_update_logged(self, client, django_user_model):
        # Need to be logged for this one
        user = django_user_model.objects.create_user(username='random', password='user')
        client.login(username='random', password='user')
        project = ProjectFactory.create(created_by=user)
        new_description = project.description + '_new'
        body = {'name': project.name, 'description': new_description}
        response = client.post(reverse("projects:project_edit", kwargs={"pk": project.id}), body)
        assert response.status_code == 302
        project.refresh_from_db()
        assert project.description == new_description
