import pytest

from toxsign.signatures.tests.factories import SignatureFactory

pytestmark = pytest.mark.django_db

def test_signature_model():
    assay = SignatureFactory.create(name='my_sig')
    assert assay.name == 'my_sig'
