import pytest

from django.urls import reverse, resolve
from django.test import Client

from toxsign.assays.tests.factories import AssayFactory

pytestmark = pytest.mark.django_db

def test_details():
    assay = AssayFactory.create()
    assert (
        reverse("assays:detail", kwargs={"assid": assay.tsx_id})
        == f"/assays/{assay.tsx_id}/"
    )
    assert resolve(f"/assays/{assay.tsx_id}/").view_name == "assays:detail"
