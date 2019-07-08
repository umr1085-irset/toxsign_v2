from factory import DjangoModelFactory, Faker, SubFactory
from toxsign.signature.models import Signature
from toxsign.projects.tests.factories import ProjectFactory
from toxsign.users.tests.factories import UserFactory
from toxsign.assays.tests.factories import FactorFactory
from toxsign.ontologies.tests.factories import *

class SignatureFactory(DjangoModelFactory):

    name = Faker("name")
    tsx_id = Faker("first_name")
    created_by = SubFactory(UserFactory)
    status = "PRIVATE"
    signature_type = "GENOMICS"
    phenotype_description = Faker("text")
    experimental_design = Faker("text")
    dev_stage = 'PREPUBERTAL'
    generation = 'F0'
    sex_type = 'BOTH'
    exp_type = 'OTHER'
    factor = SubFactory(FactorFactory)
    organism = SubFactory(SpeciesFactory)
    tissue = SubFactory(TissueFactory)
    cell = SubFactory(CellFactory)
    cell_line = SubFactory(CellLineFactory)
    chemical = SubFactory(ChemicalFactory)
    chemical_slug = Faker("text", Length=100)
    disease = SubFactory(DiseaseFactory)
    technology = SubFactory(ExperimentFactory)
    technology_slug = Faker("text", Length=100)
    platform = Faker("text")
    control_sample_number = Faker.pyfloat()
    treated_sample_number = Faker.pyfloat()
    pvalue = Faker.pyfloat()
    cutoff = Faker.pyfloat()
    statistical_processing = Faker("text")
    up_gene_file_path = Faker("text", Length=400)
    down_gene_file_path = Faker("text", Length=400)
    interrogated_gene_file_path = Faker("text", Length=400)
    additional_file_path = Faker("text", Length=400)
    gene_id = "ENTREZ"

    class Meta:
        model = Signature
