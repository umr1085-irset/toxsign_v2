import pytest

from django.urls import reverse, resolve
from django.test import Client

from toxsign.projects.tests.factories import ProjectFactory
from toxsign.users.tests.factories import UserFactory
from toxsign.groups.tests.factories import GroupFactory

from guardian.shortcuts import get_perms

pytestmark = pytest.mark.django_db


class TestProjectDetailView:

    def test_details_private_anonymous(self, client):

        project = ProjectFactory.create()
        response = client.get(reverse("projects:detail", kwargs={"prjid": project.tsx_id}))
        # This actually fails silently.. with a redirect.
        assert response.status_code == 302

    def test_details_private_logged(self, client, django_user_model):
        user = django_user_model.objects.create_user(username='random', password='user')
        client.login(username='random', password='user')
        project = ProjectFactory.create(created_by=user)
        response = client.get(reverse("projects:detail", kwargs={"prjid": project.tsx_id}))
        response_project = response.context['project']
        assert project == response_project

    def test_detail_read_groups(self, client, django_user_model):
        group = GroupFactory.create()
        project = ProjectFactory.create(read_groups=[group])
        user = django_user_model.objects.create_user(username='random', password='user')
        group.user_set.add(user)
        client.login(username='random', password='user')
        response = client.get(reverse("projects:detail", kwargs={"prjid": project.tsx_id}))
        response_project = response.context['project']
        assert project == response_project

    def test_details_public(self, client):
        project = ProjectFactory.create(status="PUBLIC")
        response = client.get(reverse("projects:detail", kwargs={"prjid": project.tsx_id}))
        response_project = response.context['project']
        assert project == response_project

class TestProjectUpdateView:

    def test_update_anonymous(self, client):
        project = ProjectFactory.create()
        new_description = project.description + '_new'
        body = {'name': project.name, 'description': new_description, 'status': "PRIVATE", 'project_type':"INTERVENTIONAL", 'save': "Save"}
        # This actually fails silently.. with a redirect.
        response = client.post(reverse("projects:project_edit", kwargs={"prjid": project.tsx_id}), body)
        assert response.status_code == 302
        project.refresh_from_db()
        assert project.description != new_description

    # Even with the edit group, users cannot edit the project
    def test_update_edit_groups(self, client, django_user_model):
        group = GroupFactory.create()
        project = ProjectFactory.create(read_groups=[group])
        user = django_user_model.objects.create_user(username='random', password='user')
        group.user_set.add(user)
        client.login(username='random', password='user')
        new_description = project.description + '_new'
        body = {'name': project.name, 'description': new_description, 'status': "PRIVATE", 'project_type':"INTERVENTIONAL", 'save': "Save"}
        response = client.post(reverse("projects:project_edit", kwargs={"prjid": project.tsx_id}), body)
        assert response.status_code == 302
        project.refresh_from_db()
        assert project.description != new_description

    def test_update_logged(self, client, django_user_model):
        # Need to be logged for this one
        user = django_user_model.objects.create_user(username='random', password='user')
        client.login(username='random', password='user')
        project = ProjectFactory.create(created_by=user)
        new_description = project.description + '_new'
        body = {'name': project.name, 'description': new_description, 'status': "PRIVATE", 'project_type':"INTERVENTIONAL", 'save': "Save"}
        response = client.post(reverse("projects:project_edit", kwargs={"prjid": project.tsx_id}), body)
        assert response.status_code == 302
        project.refresh_from_db()
        assert project.description == new_description

    # This should fail, project cannot be modified once public
    def test_update_logged_public(self, client, django_user_model):
        # Need to be logged for this one
        user = django_user_model.objects.create_user(username='random', password='user')
        client.login(username='random', password='user')
        project = ProjectFactory.create(created_by=user, status='PUBLIC')
        new_description = project.description + '_new'
        body = {'name': project.name, 'description': new_description, 'status': "PRIVATE", 'project_type':"INTERVENTIONAL", 'save': "Save"}
        response = client.post(reverse("projects:project_edit", kwargs={"prjid": project.tsx_id}), body)
        print(response.status_code)
        assert response.status_code == 302
        project.refresh_from_db()
        assert project.description != new_description
