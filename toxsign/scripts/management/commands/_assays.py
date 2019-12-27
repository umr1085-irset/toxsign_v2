import bson
from ._users import get_owner
from ._ontologies import get_ontology, get_ontology_slug
from toxsign.assays.models import Assay

def process_assays(path, study_dict, user_dict, project_dict):

    with open(path,'rb') as f:
        data = bson.decode_all(f.read())

    treated_number = 1
    fake_assays = 0
    assay_list = []
    onto_dict = {}
    data = sorted(data, key=lambda k:int(k['id'].split("TSA")[-1]))

    for assay in data:
        id = int(assay['id'].split("TSA")[-1])
        while not id == treated_number:
            if treated_number > id:
                raise Exception("Something went wrong when creating fake assays")
            assay_list.append(_create_fake_assay("TSA" + str(treated_number), user_dict))
            fake_assays += 1
            treated_number +=1
        newassay, onto_dict = _create_assay(assay, study_dict, user_dict, project_dict, onto_dict)
        assay_list.append(newassay)
        treated_number +=1

    if not (treated_number -1) == (len(data) + fake_assays):
        print(fake_assays)
        print(treated_number)
        print(len(data))
        raise Exception("Missing!")

    # Bulk create
    Assay.objects.bulk_create(assay_list)
    _cleanup()

def get_assay_dict():
    dict = {}
    for assay in Assay.objects.all():
        dict[assay.tsx_id] = assay
    return dict

def _cleanup():
    Assay.objects.filter(name='temp_assay_delete_me').delete()

def _create_fake_assay(assay_id, user_dict):
    return Assay(**{'tsx_id': assay_id, 'created_by': user_dict['admin'], 'name': 'temp_assay_delete_me'})

def _create_assay(assay_data, study_dict, user_dict, project_dict, onto_dict):

    owner = get_owner(assay_data['owner'], user_dict)
    # Need to get the project id and the ontologies
    study_id = assay_data['studies']
    study_data = study_dict[study_id]

    dev_dict = {'': 'NA', 'Adulthood': 'ADULTHOOD', 'Jurkat cells':'NA', 'NA':'NA', 'Ishikawa cells':'NA', 'MCF-7':'NA', 'primary hepatocytes':'NA', 'HK-2':'NA'}
    gen_dict = {'': 'NA', 'NA': 'NA', 'f0': 'F0'}
    sex_dict = {'Male':'MALE', '': 'NA', 'NA':'NA', 'Both':'BOTH', 'Female':'FEMALE'}
    exp_dict = {'':'NA', 'in vitro':'INVITRO', 'NA':'NA', 'in vivo':'INVIVO', 'Female':'NA', 'Male':'NA', 'ex vivo':'EXVIVO'}

    assay_dict = {
        'name': assay_data['title'],
        'tsx_id':  assay_data['id'],
        'created_by': owner,
        'description': study_data['description'],
        'experimental_design': study_data['experimental_design'],
        'results': study_data['results'],
        'additional_info': assay_data['additional_information'],
        'dev_stage': dev_dict[assay_data['developmental_stage']],
        'generation': gen_dict[assay_data['generation']],
        'sex_type': sex_dict[assay_data['sex']],
        'exp_type': exp_dict[assay_data['experimental_type']],
        'project': project_dict[assay_data['projects']],
    }

    assay_dict['organism'], onto_dict = get_ontology("Species", assay_data, "organism", onto_dict)
    assay_dict['tissue'], onto_dict = get_ontology("Tissue", assay_data, "tissue", onto_dict)
    assay_dict['cell'], onto_dict = get_ontology("Cell", assay_data, "cell", onto_dict)
    assay_dict['cell_line'], assay_dict['cell_line_slug'], onto_dict = get_ontology_slug("CellLine", assay_data, "cell_line", "cell_line_slug", onto_dict)
    assay = Assay(**assay_dict)

    return assay, onto_dict
