import pytest

from django.urls import reverse, resolve
from django.test import Client

from toxsign.studies.tests.factories import StudyFactory

pytestmark = pytest.mark.django_db

def test_list():
    assert reverse("studies:index") == ""
    assert resolve("").view_name == "studies:index"

def test_details():
    study = StudyFactory.create()
    assert (
        reverse("studies:detail", kwargs={"stdid": study.tsx_id})
        == f"{study.tsx_id}/"
    )
    assert resolve(f"{study.tsx_id}/").view_name == "studies:detail"

def test_update():
    study = StudyFactory.create()
    assert (
        reverse("studies:study_edit", kwargs={"pk": study.id})
        == f"study_edit/{study.id}/"
    )
    assert resolve(f"study_edit/{study.id}/").view_name == "studies:study_edit"