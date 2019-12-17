import pytest

from django.urls import reverse, resolve
from django.test import Client

from toxsign.projects.tests.factories import ProjectFactory
from toxsign.users.tests.factories import UserFactory
from toxsign.assays.tests.factories import AssayFactory, FactorFactory
from toxsign.signatures.tests.factories import SignatureFactory
from toxsign.groups.tests.factories import GroupFactory

from toxsign.signatures.models import Signature

from guardian.shortcuts import get_perms

pytestmark = pytest.mark.django_db


class TestSignatureCreateView:

    def test_create_owner(self, client, django_user_model):
        user = django_user_model.objects.create_user(username='random', password='user')
        client.login(username='random', password='user')
        project = ProjectFactory.create(created_by=user)
        assay = AssayFactory.create(project=project)
        factor = FactorFactory.create(assay=assay)
        response = get_create_form(client, project.tsx_id)
        assert response.status_code == 200
#        response = create(client, project.tsx_id, response.context['form'], 'random', factor=factor)
        response = create(client, project.tsx_id, response.context['form'], 'random')
        assert response.status_code == 302
        assert Signature.objects.filter(name='random').count() == 1

class TestSignatureDetailView:

    def test_details_private_anonymous(self, client):
        sig = SignatureFactory.create()
        response = client.get(reverse("signatures:detail", kwargs={"sigid": sig.tsx_id}))
        # This actually fails silently.. with a redirect.
        assert response.status_code == 302

    def test_details_private_logged(self, client, django_user_model):
        user = django_user_model.objects.create_user(username='random', password='user')
        client.login(username='random', password='user')
        project = ProjectFactory.create(created_by=user)
        assay = AssayFactory.create(project=project)
        factor = FactorFactory.create(assay=assay)
        sig = SignatureFactory.create(factor=factor)
        response = client.get(reverse("signatures:detail", kwargs={"sigid": sig.tsx_id}))
        assert response.status_code == 200
        response_signature = response.context['signature']
        assert sig == response_signature

    def test_detail_read_groups(self, client, django_user_model):
        group = GroupFactory.create()
        project = ProjectFactory.create(read_groups=[group])
        user = django_user_model.objects.create_user(username='random', password='user')
        group.user_set.add(user)
        assay = AssayFactory.create(project=project)
        factor = FactorFactory.create(assay=assay)
        sig = SignatureFactory.create(factor=factor)
        client.login(username='random', password='user')
        response = client.get(reverse("signatures:detail", kwargs={"sigid": sig.tsx_id}))
        assert response.status_code == 200
        response_signature = response.context['signature']
        assert sig == response_signature

    def test_details_public(self, client):
        project = ProjectFactory.create(status="PUBLIC")
        assay = AssayFactory.create(project=project)
        factor = FactorFactory.create(assay=assay)
        sig = SignatureFactory.create(factor=factor)
        response = client.get(reverse("signatures:detail", kwargs={"sigid": sig.tsx_id}))
        assert response.status_code == 200
        response_signature = response.context['signature']
        assert sig == response_signature

class TestSignatureUpdateView:

    def test_update_anonymous(self, client):
        sig = SignatureFactory.create()
        # If not access, not form is sent. Instead, it redirect
        response = get_update_form(client, sig.tsx_id)
        assert response.status_code == 302

    def test_update_edit_groups(self, client, django_user_model):
        user = django_user_model.objects.create_user(username='random', password='user')
        group = GroupFactory.create()
        project = ProjectFactory.create(edit_groups=[group])
        assay = AssayFactory.create(project=project)
        factor = FactorFactory.create(assay=assay)
        sig = SignatureFactory.create(factor=factor)
        new_name = sig.name + '_new'
        group.user_set.add(user)
        client.login(username='random', password='user')
        response = get_update_form(client, sig.tsx_id)
        assert 'form' in response.context
        assert response.status_code == 200
        form = response.context['form']
        response = update(client, sig.tsx_id, form, new_name)
        assert response.status_code == 302
        sig.refresh_from_db()
        assert sig.name == new_name

    def test_update_logged(self, client, django_user_model):
        # Need to be logged for this one
        user = django_user_model.objects.create_user(username='random', password='user')
        project = ProjectFactory.create(created_by=user)
        assay = AssayFactory.create(project=project)
        factor = FactorFactory.create(assay=assay)
        sig = SignatureFactory.create(factor=factor)
        new_name = sig.name + '_new'
        client.login(username='random', password='user')
        response = get_update_form(client, sig.tsx_id)
        assert 'form' in response.context
        assert response.status_code == 200
        form = response.context['form']
        response = update(client, sig.tsx_id, form, new_name)
        assert response.status_code == 302
        sig.refresh_from_db()
        assert sig.name == new_name

    # This should fail, assay cannot be modified once public
    def test_update_logged_public(self, client, django_user_model):
        # Need to be logged for this one
        user = django_user_model.objects.create_user(username='random', password='user')
        client.login(username='random', password='user')
        project = ProjectFactory.create(created_by=user, status='PUBLIC')
        assay = AssayFactory.create(project=project)
        factor = FactorFactory.create(assay=assay)
        sig = SignatureFactory.create(factor=factor)
        response = get_update_form(client, sig.tsx_id)
        assert response.status_code == 302

def get_create_form(client, tsx_id):
        update_url = reverse("signatures:signature_create", kwargs={"prjid": tsx_id})
        return client.get(update_url)

def get_update_form(client, tsx_id):
        update_url = reverse("signatures:signature_edit", kwargs={"sigid": tsx_id})
        return client.get(update_url)

def create(client, tsx_id, form, name, factor=None):
        data = form.initial
        data['name'] = name
        data['signature_type'] = "GENOMICS"
        data['dev_stage'] = "FETAL"
        data['generation'] = "F1"
        data['sex_type'] = "MALE"
        data['exp_type'] = "EXVIVO"
        data['gene_id'] = "ENTREZ"
        if factor:
            data['factor'] = factor.id
        update_url = reverse("signatures:signature_create", kwargs={"prjid": tsx_id})
        return client.post(update_url, data)

def update(client, tsx_id, form, new_name):
        data = form.initial
        data['name'] = new_name
        # Need to clear empty values  and filepath
        data.pop('up_gene_file_path')
        data.pop('down_gene_file_path')
        data.pop('interrogated_gene_file_path')
        data.pop('additional_file_path')
        data = {k: v for k, v in data.items() if v is not None}
        update_url = reverse("signatures:signature_edit", kwargs={"sigid": tsx_id})
        return client.post(update_url, data)
