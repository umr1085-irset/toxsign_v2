import pytest

from django.urls import reverse, resolve
from django.test import Client

from toxsign.projects.tests.factories import ProjectFactory
from toxsign.users.tests.factories import UserFactory
from toxsign.assays.tests.factories import AssayFactory, FactorFactory
from toxsign.groups.tests.factories import GroupFactory

from guardian.shortcuts import get_perms

pytestmark = pytest.mark.django_db


class TestAssayDetailView:

    def test_details_private_anonymous(self, client):
        factor = FactorFactory.create()
        response = client.get(reverse("assays:factor_detail", kwargs={"facid": factor.tsx_id}))
        # This actually fails silently.. with a redirect.
        assert response.status_code == 302

    def test_details_private_logged(self, client, django_user_model):
        user = django_user_model.objects.create_user(username='random', password='user')
        client.login(username='random', password='user')
        project = ProjectFactory.create(created_by=user)
        assay = AssayFactory.create(project=project)
        factor = FactorFactory.create(assay=assay)
        response = client.get(reverse("assays:factor_detail", kwargs={"facid": factor.tsx_id}))
        assert response.status_code == 200
        response_factor = response.context['factor']
        assert factor == response_factor

    def test_detail_read_groups(self, client, django_user_model):
        group = GroupFactory.create()
        project = ProjectFactory.create(read_groups=[group])
        user = django_user_model.objects.create_user(username='random', password='user')
        group.user_set.add(user)
        assay = AssayFactory.create(project=project)
        factor =  FactorFactory.create(assay=assay)
        client.login(username='random', password='user')
        response = client.get(reverse("assays:factor_detail", kwargs={"facid": factor.tsx_id}))
        assert response.status_code == 200
        response_factor = response.context['factor']
        assert factor == response_factor

    def test_details_public(self, client):
        project = ProjectFactory.create(status="PUBLIC")
        assay = AssayFactory.create(project=project)
        factor =  FactorFactory.create(assay=assay)
        response = client.get(reverse("assays:factor_detail", kwargs={"facid": factor.tsx_id}))
        assert response.status_code == 200
        response_factor = response.context['factor']
        assert factor == response_factor

class TestAssayUpdateView:

    def test_update_anonymous(self, client):
        factor = FactorFactory.create()
        response = get_form(client, factor.tsx_id)
        assert response.status_code == 302

    def test_update_edit_groups(self, client, django_user_model):
        group = GroupFactory.create()
        project = ProjectFactory.create(edit_groups=[group])
        assay = AssayFactory.create(project=project)
        factor = FactorFactory.create(assay=assay)
        user = django_user_model.objects.create_user(username='random', password='user')
        group.user_set.add(user)
        client.login(username='random', password='user')
        new_name = factor.name + '_new'
        response = get_form(client, factor.tsx_id)
        assert response.status_code == 200
        assert 'form' in response.context
        response = update(client, factor.tsx_id, response.context['form'], new_name)
        assert response.status_code == 302
        factor.refresh_from_db()
        assert factor.name == new_name

    def test_update_logged(self, client, django_user_model):
        # Need to be logged for this one
        user = django_user_model.objects.create_user(username='random', password='user')
        client.login(username='random', password='user')
        project = ProjectFactory.create(created_by=user)
        assay = AssayFactory.create(project=project)
        factor = FactorFactory.create(assay=assay)
        new_name = factor.name + '_new'
        response = get_form(client, factor.tsx_id)
        assert response.status_code == 200
        assert 'form' in response.context
        response = update(client, factor.tsx_id, response.context['form'], new_name)
        assert response.status_code == 302
        factor.refresh_from_db()
        assert factor.name == new_name

    # This should fail, assay cannot be modified once public
    def test_update_logged_public(self, client, django_user_model):
        # Need to be logged for this one
        user = django_user_model.objects.create_user(username='random', password='user')
        client.login(username='random', password='user')
        project = ProjectFactory.create(created_by=user, status='PUBLIC')
        assay = AssayFactory.create(project=project)
        factor = FactorFactory.create(assay=assay)
        response = get_form(client, factor.tsx_id)
        assert response.status_code == 302

def get_form(client, tsx_id):
        update_url = reverse("assays:factor_edit", kwargs={"facid": tsx_id})
        return client.get(update_url)

def update(client, tsx_id, form, new_name):
        data = form.initial
        data['name'] = new_name
        update_url = reverse("assays:factor_edit", kwargs={"facid": tsx_id})
        return client.post(update_url, data)
