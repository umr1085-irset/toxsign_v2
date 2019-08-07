import pytest

from django.urls import reverse, resolve
from django.test import Client

from toxsign.assays.tests.factories import AssayFactory, FactorFactory

pytestmark = pytest.mark.django_db

def test_assay_details():
    assay = AssayFactory.create()
    assert (
        reverse("assays:assay_detail", kwargs={"assid": assay.tsx_id})
        == f"/assays/assay/{assay.tsx_id}/"
    )
    assert resolve(f"/assays/assay/{assay.tsx_id}/").view_name == "assays:assay_detail"

def test_factor_details():
    factor = FactorFactory.create()
    assert (
        reverse("assays:factor_detail", kwargs={"facid": factor.tsx_id})
        == f"/assays/factor/{factor.tsx_id}/"
    )
    assert resolve(f"/assays/factor/{factor.tsx_id}/").view_name == "assays:factor_detail"
