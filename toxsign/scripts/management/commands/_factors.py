import bson
from ._users import get_owner
from ._ontologies import get_ontology, get_ontology_slug
from toxsign.assays.models import Factor, ChemicalsubFactor


def process_factors(path, user_dict, assay_dict):

    with open(path,'rb') as f:
        data = bson.decode_all(f.read())

    treated_number = 1
    fake_factors = 0
    factor_list = []
    subfactor_list = []
    onto_dict = {}
    data = sorted(data, key=lambda k:int(k['id'].split("TSF")[-1]))

    for factor in data:
        id = int(factor['id'].split("TSF")[-1])
        while not id == treated_number:
            if treated_number > id:
                raise Exception("Something went wrong when creating fake factors")
            factor_list.append(_create_fake_factor("TSF" + str(treated_number), user_dict))
            fake_factors += 1
            treated_number +=1

        factor_list.append(_create_factor(factor, user_dict, assay_dict))
        treated_number +=1

    if not (treated_number -1) == (len(data) + fake_factors):
        print(fake_factors)
        print(treated_number)
        print(len(data))
        raise Exception("Missing!")

    # Bulk create

    Factor.objects.bulk_create(factor_list)

    factor_dict = get_factor_dict()

    for factor in data:
        subfactor, onto_dict = _create_sub_factor(factor, user_dict, factor_dict, onto_dict)
        subfactor_list.append(subfactor)

    ChemicalsubFactor.objects.bulk_create(subfactor_list)
    _cleanup()

def get_factor_dict():
    dict = {}
    for factor in Factor.objects.all():
        dict[factor.tsx_id] = factor
    return dict

def get_corres_dict():
    dict = {}
    for factor in Factor.objects.all():
        if factor.assay:
            dict[factor.assay.tsx_id] = factor
    return dict

def _create_fake_factor(factor_id, user_dict):
    factor_dict = {'tsx_id': factor_id, 'created_by': user_dict['admin'], 'name': 'temp_factor_delete_me'}
    return Factor(**factor_dict)

def _cleanup():
    Factor.objects.filter(name='temp_factor_delete_me').delete()

def _create_factor(factor_data, user_dict, assay_dict):

    owner = get_owner(factor_data['owner'], user_dict)
    factor_dict = {
        'name': _get_factor_name(factor_data),
        'tsx_id':  factor_data['id'],
        'created_by': owner,
        'assay': assay_dict[factor_data['assays']]
    }

    return Factor(**factor_dict)

def _create_sub_factor(factor_data, user_dict, factor_dict, onto_dict):

    owner = get_owner(factor_data['owner'], user_dict)

    sub_fact = {
        "factor": factor_dict[factor_data['id']],
        "route": factor_data['route'],
        "vehicule" : factor_data['vehicle'],
        "exposure_time": _get_exposure_duration(factor_data),
        "exposure_frequencie": factor_data['exposure_frequencies'],
        "additional_info": factor_data['additional_information']
    }
    sub_fact["dose_value"], sub_fact["dose_unit"] =  _get_dose(factor_data)
    sub_fact["chemical"], sub_fact["chemical_slug"], onto_dict = get_ontology_slug("Chemical", factor_data, "chemical", "chemical_slug", onto_dict, "CAS")

    return ChemicalsubFactor(**sub_fact), onto_dict

def _get_factor_name(factor_data):

    li = factor_data['chemical'].split("CAS")
    if not li[0]:
        if not factor_data['chemical_name']:
            return factor_data['id']
        else:
            return factor_data['chemical_name']
    else:
        return li[0]

def _get_dose(factor_data):

    dose_unit_dict = {
        "microgkg": "µg/kg",
        "uM": "µM",
        "mg/ml": "mg/mL",
        "µM": "µM",
        "mgmL": "mg/mL",
        "mM": "mM",
        "pM": "pM",
        "mg/kg": "mg/kg",
        "fM": "fM",
        "nM": "nM",
        "microM": "µM",
        "ug/kg": "µg/kg",
        "microgmL": "µg/mL",
        "ngmL": "ng/mL"
    }

    dose = factor_data['dose']
    li = dose.split(" ")
    if len(li) > 2:
        return 0, "NA"
    if li[0] == "0":
        return  0, "NA"
    if li[0] == "IC10":
        return 10, "IC"
    else:
        return float(li[0]), dose_unit_dict[li[-1]]

def _get_exposure_duration(factor_data):

    exposure_duration = factor_data['exposure_duration']
    li = exposure_duration.split(" ")

    value = float(li[0])
    if li[-1] in ["days","day"]:
        value = value * 24
    return value

