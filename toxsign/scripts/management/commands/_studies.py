import bson

def process_studies(path):

    # Return a dict with project_id -> studies values
    with open(path,'rb') as f:
        data = bson.decode_all(f.read())

    dict = {}
    for study in data:
        sub_dict = {
            'experimental_design': study['experimental_design'],
            'description': study['description'],
            'results': study['results']
        }
        dict[study['id']] = sub_dict

    return dict
