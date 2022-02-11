from factory import DjangoModelFactory, Faker, SubFactory
from toxsign.assays.models import Assay, Factor, ChemicalsubFactor
from toxsign.projects.tests.factories import ProjectFactory
from toxsign.users.tests.factories import UserFactory
from toxsign.projects.tests.factories import ProjectFactory
from toxsign.ontologies.tests.factories import *

class AssayFactory(DjangoModelFactory):

    name = Faker("name")
    tsx_id = Faker("first_name")
    created_by = SubFactory(UserFactory)
    additional_info = Faker("text")
    experimental_design = Faker("text")
    dev_stage = 'PREPUBERTAL'
    generation = 'F0'
    sex_type = 'BOTH'
    exp_type = 'OTHER'
    project = SubFactory(ProjectFactory)
    organism = SubFactory(SpeciesFactory)
    tissue = SubFactory(TissueFactory)
    cell = SubFactory(CellFactory)
    cell_line = SubFactory(CellLineFactory)
    class Meta:
        model = Assay

class FactorFactory(DjangoModelFactory):

    name = Faker("name")
    tsx_id = Faker("first_name")
    created_by = SubFactory(UserFactory)
    assay = SubFactory('toxsign.assays.tests.factories.AssayFactory')
    # No status?
    class Meta:
        model = Factor

class ChemicalsubFactorFactory(DjangoModelFactory):

    created_by = SubFactory(UserFactory)
    chemical = SubFactory(ChemicalFactory)
    chemical_slug = Faker("first_name")
    route = Faker("first_name")
    vehicule = Faker("first_name")
    dose_value = Faker("pyfloat")
    dose_unit = "mM"
    exposure_time = Faker("pyfloat")
    exposure_frequencie = Faker("first_name")
    additional_info = Faker("text")
    factor = SubFactory('toxsign.assays.tests.factories.FactorFactory')
    # No status?
    class Meta:
        model = ChemicalsubFactor
