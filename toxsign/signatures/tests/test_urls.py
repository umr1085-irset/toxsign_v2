import pytest

from django.urls import reverse, resolve
from django.test import Client

from toxsign.signatures.tests.factories import SignatureFactory

pytestmark = pytest.mark.django_db

def test_list():
    assert reverse("signatures:index") == "/signatures/"
    assert resolve("/signatures/").view_name == "signatures:index"

def test_details():
    signature = SignatureFactory.create()
    assert (
        reverse("signatures:detail", kwargs={"sigid": signature.tsx_id})
        == f"/signatures/{signature.tsx_id}/"
    )
    assert resolve(f"/signatures/{signature.tsx_id}/").view_name == "signatures:detail"
