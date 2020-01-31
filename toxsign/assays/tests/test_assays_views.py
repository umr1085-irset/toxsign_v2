import pytest

from django.urls import reverse, resolve
from django.test import Client

from toxsign.projects.tests.factories import ProjectFactory
from toxsign.users.tests.factories import UserFactory
from toxsign.assays.tests.factories import AssayFactory
from toxsign.groups.tests.factories import GroupFactory

from guardian.shortcuts import get_perms

pytestmark = pytest.mark.django_db


class TestAssayDetailView:

    def test_details_private_anonymous(self, client):
        assay = AssayFactory.create()
        response = client.get(reverse("assays:assay_detail", kwargs={"assid": assay.tsx_id}))
        # This actually fails silently.. with a redirect.
        assert response.status_code == 302

    def test_details_private_logged(self, client, django_user_model):
        user = django_user_model.objects.create_user(username='random', password='user')
        client.login(username='random', password='user')
        project = ProjectFactory.create(created_by=user)
        assay = AssayFactory.create(project=project)
        response = client.get(reverse("assays:assay_detail", kwargs={"assid": assay.tsx_id}))
        assert response.status_code == 200
        response_assay = response.context['assay']
        assert assay == response_assay

    def test_detail_read_groups(self, client, django_user_model):
        group = GroupFactory.create()
        project = ProjectFactory.create(read_groups=[group])
        user = django_user_model.objects.create_user(username='random', password='user')
        group.user_set.add(user)
        assay = AssayFactory.create(project=project)
        client.login(username='random', password='user')
        response = client.get(reverse("assays:assay_detail", kwargs={"assid": assay.tsx_id}))
        assert response.status_code == 200
        response_assay = response.context['assay']
        assert assay == response_assay

    def test_details_public(self, client):
        project = ProjectFactory.create(status="PUBLIC")
        assay = AssayFactory.create(project=project)
        response = client.get(reverse("assays:assay_detail", kwargs={"assid": assay.tsx_id}))
        assert response.status_code == 200
        response_assay = response.context['assay']
        assert assay == response_assay

class TestAssayUpdateView:

    def test_update_anonymous(self, client):
        assay = AssayFactory.create()
        new_description = assay.description + '_new'
        # If not access, not form is sent. Instead, it redirect
        response = get_form(client, assay.tsx_id)
        assert response.status_code == 302

    def test_update_edit_groups(self, client, django_user_model):
        group = GroupFactory.create()
        project = ProjectFactory.create(edit_groups=[group])
        assay = AssayFactory.create(project=project)
        user = django_user_model.objects.create_user(username='random', password='user')
        group.user_set.add(user)
        client.login(username='random', password='user')
        new_description = assay.description + '_new'
        response = get_form(client, assay.tsx_id)
        assert 'form' in response.context
        assert response.status_code == 200
        form = response.context['form']
        response = update(client, assay.tsx_id, form, new_description)
        assert response.status_code == 302
        assay.refresh_from_db()
        assert assay.description == new_description

    def test_update_logged(self, client, django_user_model):
        # Need to be logged for this one
        user = django_user_model.objects.create_user(username='random', password='user')
        client.login(username='random', password='user')
        project = ProjectFactory.create(created_by=user)
        assay = AssayFactory.create(project=project)
        new_description = assay.description + '_new'
        response = get_form(client, assay.tsx_id)
        assert 'form' in response.context
        assert response.status_code == 200
        form = response.context['form']
        response = update(client, assay.tsx_id, form, new_description)
        assert response.status_code == 302
        assay.refresh_from_db()
        assert assay.description == new_description

    # This should fail, assay cannot be modified once public
    def test_update_logged_public(self, client, django_user_model):
        # Need to be logged for this one
        user = django_user_model.objects.create_user(username='random', password='user')
        client.login(username='random', password='user')
        project = ProjectFactory.create(created_by=user, status='PUBLIC')
        assay = AssayFactory.create(project=project)
        response = get_form(client, assay.tsx_id)
        assert response.status_code == 302

def get_form(client, tsx_id):
        update_url = reverse("assays:assay_edit", kwargs={"assid": tsx_id})
        return client.get(update_url)

def update(client, tsx_id, form, new_description):
        data = form.initial
        data['description'] = new_description
        update_url = reverse("assays:assay_edit", kwargs={"assid": tsx_id})
        return client.post(update_url, data)
