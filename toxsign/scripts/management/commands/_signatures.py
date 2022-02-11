import bson
import os
from ._users import get_owner
from ._ontologies import get_ontology, get_ontology_slug
from toxsign.signatures.models import Signature
from django.core.files import File

def process_signatures(path, user_dict, corresp_dict):

    with open(path,'rb') as f:
        data = bson.decode_all(f.read())

    treated_number = 1
    fake_signatures = 0
    signature_list = []
    onto_dict = {}
    data = sorted(data, key=lambda k:int(k['id'].split("TSS")[-1]))

    for signature in data:
        id = int(signature['id'].split("TSS")[-1])
        while not id == treated_number:
            if treated_number > id:
                raise Exception("Something went wrong when creating fake signatures")
            signature_list.append(_create_fake_signature("TSS" + str(treated_number), user_dict))
            fake_signatures += 1
            treated_number +=1

        newsignature, onto_dict = _create_signature(signature, user_dict, corresp_dict, onto_dict)
        signature_list.append(newsignature)
        treated_number +=1

    if not (treated_number -1) == (len(data) + fake_signatures):
        print(fake_signatures)
        print(treated_number)
        print(len(data))
        raise Exception("Missing!")

    # Bulk create
    Signature.objects.bulk_create(signature_list)
    _cleanup()

def populate_signatures(path, file_root):

    with open(path,'rb') as f:
        data = bson.decode_all(f.read())

    for signature in data:
        _populate_signature(signature, file_root)

def _create_fake_signature(signature_id, user_dict):
    return Signature(**{'tsx_id': signature_id, 'created_by': user_dict['admin'], 'name': 'temp_signature_delete_me'})

def _cleanup():
    Signature.objects.filter(name='temp_signature_delete_me').delete()

def _create_signature(signature_data, user_dict, corresp_dict, onto_dict):

    owner = get_owner(signature_data['owner'], user_dict)

    dev_dict = {'': 'NA', 'Adulthood': 'ADULTHOOD', 'Jurkat cells':'NA', 'NA':'NA', 'Ishikawa cells':'NA', 'MCF-7':'NA', 'primary hepatocytes':'NA', 'HK-2':'NA', 'Fetal': 'FETAL'}
    gen_dict = {'': 'NA', 'NA': 'NA', 'f0': 'F0', 'f1': 'F1'}
    sex_dict = {'Male':'MALE', '': 'NA', 'NA':'NA', 'Both':'BOTH', 'Female':'FEMALE'}

    sig_dict = {
        'name': signature_data['title'],
        'tsx_id':  signature_data['id'],
        'created_by': owner,
        'signature_type': "GENOMIC",
        'phenotype_description': signature_data['observed_effect'],
        'dev_stage': dev_dict[signature_data['developmental_stage']],
        'generation': gen_dict[signature_data['generation']],
        'sex_type': sex_dict[signature_data['sex']],
        'factor': corresp_dict[signature_data['assays']],
        'platform': signature_data['plateform'],
        'control_sample_number':  _get_numerical_values("int", signature_data['control_sample']),
        'treated_sample_number': _get_numerical_values("int", signature_data['treated_sample']),
        'pvalue': _get_numerical_values("float", signature_data['pvalue']),
        'cutoff': _get_numerical_values("float", signature_data['cutoff']),
        'statistical_processing': signature_data['statistical_processing'],
    }

    sig_dict['organism'], onto_dict = get_ontology("Species", signature_data, "organism", onto_dict)
    sig_dict['tissue'], onto_dict = get_ontology("Tissue", signature_data, "tissue", onto_dict)
    sig_dict['cell'], onto_dict = get_ontology("Cell", signature_data, "cell", onto_dict)
    sig_dict['cell_line'], sig_dict['cell_line_slug'], onto_dict = get_ontology_slug("CellLine", signature_data, "cell_line", "cell_line_slug", onto_dict)
    sig_dict['disease'], onto_dict = get_ontology("Disease", signature_data, "pathology", onto_dict)

    sig_dict['technology'], sig_dict['technology_slug'], onto_dict = get_ontology_slug("Experiment", signature_data, "technology", "technology_slug", onto_dict)
    return Signature(**sig_dict), onto_dict

def _populate_signature(signature, file_root):
    # Get signature
    if signature['id'] == "TSS8492":
        print("Skipping " +  signature['id'])
        return

    if not os.path.exists("{}/{}".format(file_root, signature['projects'])) or not os.path.exists("{}/{}/{}".format(file_root, signature['projects'], signature['id'])):
        print("Missing folder for signature " +  signature['id'] + ", skipping")
        return

    if not os.path.exists("{}/{}/{}/{}".format(file_root, signature['projects'], signature['id'], signature['file_interrogated'])):
        print("Missing  interrogated file, skipping " +  signature['id'])
        return

    if not os.path.exists("{}/{}/{}/{}".format(file_root, signature['projects'], signature['id'], signature['file_up'])):
        open("{}/{}/{}/{}".format(file_root, signature['projects'], signature['id'], signature['file_up']), 'a').close()

    if not os.path.exists("{}/{}/{}/{}".format(file_root, signature['projects'], signature['id'], signature['file_down'])):
        open("{}/{}/{}/{}".format(file_root, signature['projects'], signature['id'], signature['file_down']), 'a').close()

    sig = Signature.objects.get(tsx_id=signature['id'])

    sig.up_gene_file_path.save(signature['file_up'], File(open("{}/{}/{}/{}".format(file_root, signature['projects'], signature['id'], signature['file_up']))), save=False)
    sig.down_gene_file_path.save(signature['file_down'], File(open("{}/{}/{}/{}".format(file_root, signature['projects'], signature['id'], signature['file_down']))), save=False)
    sig.interrogated_gene_file_path.save(signature['file_interrogated'], File(open("{}/{}/{}/{}".format(file_root, signature['projects'], signature['id'], signature['file_interrogated']))), save=False)
    if signature['additional_file']:
        sig.additional_file_path.save(signature['file_up'], File(open("{}/{}/{}/{}".format(file_root, signature['projects'], signature['id'], signature['file_up']))), save=False)
    sig.save(force=True)

def _get_numerical_values(type, value, default=None):
    try:
        if not value:
            return default
        if type == "float":
            return float(value.replace(',','.'))
        if type == "int":
            return round(float(value.replace(',','.')))
    except:
        return default




