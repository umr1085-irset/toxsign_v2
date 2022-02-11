import pytest

from toxsign.assays.tests.factories import *

pytestmark = pytest.mark.django_db

def test_assay_model():
    assay = AssayFactory.create(name='my_assay')
    assert assay.name == 'my_assay'

def test_factor_model():
    factor = FactorFactory.create(name='my_factor')
    assert factor.name == 'my_factor'

def test_chemical_subfactor_model():
    subfactor = ChemicalsubFactorFactory.create(chemical_slug="Methamphetamines")
    assert subfactor.chemical_slug == "Methamphetamines"
