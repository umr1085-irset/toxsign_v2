from factory import DjangoModelFactory, Faker, SubFactory
from toxsign.signatures.models import Signature
from toxsign.projects.tests.factories import ProjectFactory
from toxsign.users.tests.factories import UserFactory
from toxsign.assays.tests.factories import FactorFactory
from toxsign.ontologies.tests.factories import *


class SignatureFactory(DjangoModelFactory):

    name = Faker("name")
    tsx_id = Faker("first_name")
    created_by = SubFactory(UserFactory)
    signature_type = "GENOMICS"
    phenotype_description = Faker("text")
    experimental_design = Faker("text")
    dev_stage = 'PREPUBERTAL'
    generation = 'F0'
    sex_type = 'BOTH'
    exp_type = 'OTHER'
    factor = SubFactory(FactorFactory)
    chemical_slug = Faker("text", max_nb_chars=100)
    technology_slug = Faker("text", max_nb_chars=100)
    platform = Faker("text", max_nb_chars=100)
    control_sample_number = Faker("pyint")
    treated_sample_number = Faker("pyint")
    pvalue = Faker("pyfloat")
    cutoff = Faker("pyfloat")
    statistical_processing = Faker("text")
    gene_id = "ENTREZ"


    class Meta:
        model = Signature
