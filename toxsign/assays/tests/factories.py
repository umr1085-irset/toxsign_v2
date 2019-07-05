from factory import DjangoModelFactory, Faker, SubFactory
from toxsign.assays.models import Assay, Factor
from toxsign.projects.tests.factories import ProjectFactory
from toxsign.users.tests.factories import UserFactory
from toxsign.studies.tests.factories import StudyFactory
from toxsign.ontologies.tests.factories import *

class AssayFactory(DjangoModelFactory):

    name = Faker("name")
    tsx_id = Faker("first_name")
    created_by = SubFactory(UserFactory)
    status = "PRIVATE"
    additional_info = Faker("text")
    description = Faker("text")
    experimental_design = Faker("text")
    dev_stage = 'PREPUBERTAL'
    generation = 'F0'
    sex_type = 'BOTH'
    exp_type = 'OTHER'
    prj_subClass = SubFactory(ProjectFactory)
    results = Faker("text")
    std_subClass = SubFactory(StudyFactory)
    organism = SubFactory(SpeciesFactory)
    tissue = SubFactory(TissueFactory)
    cell = SubFactory(CellFactory)
    cell_ligne = SubFactory(CellLineFactory)
    class Meta:
        model = Assay

class FactorFactory(DjangoModelFactory):

    name = Faker("name")
    tsx_id = Faker("first_name")
    created_by = SubFactory(UserFactory)
    chemical = SubFactory(ChemicalFactory)
    chemical_slug = Faker("first_name")
    factor_type = 'BIOLOGICAL'
    route = Faker("first_name")
    vehicule = Faker("first_name")
    dose_value = Faker("pyfloat")
    dose_unit = "mM"
    exposure_time = Faker("pyfloat")
    exposure_frequencie = Faker("first_name")
    additional_info = Faker("text")
    prj_subClass = SubFactory(ProjectFactory)
    std_subClass = SubFactory(StudyFactory)
    ass_subClass = SubFactory('toxsign.assay.tests.factories.AssayFactory')
    # No status?
    class Meta:
        model = Factor
