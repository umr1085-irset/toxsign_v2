from users import process_users, get_user_dict
from projects import process_projects, get_project_dict
from studies import process_studies
from assays import process_assays, get_assay_dict
from factors import process_factors, get_corres_dict
from signatures import process_signatures, populate_signatures

process_users('files/bson_files/users.bson')
users = get_user_dict()
studies = process_studies('files/bson_files/studies.bson')
process_projects('files/bson_files/projects.bson', users)
projects = get_project_dict()
process_assays('files/bson_files/assays.bson', studies, users, projects)
assays = get_assay_dict()
process_factors('files/bson_files/factors.bson',  users, assays)
corresp = get_corres_dict()
process_signatures('files/bson_files/signatures.bson', users, corresp)
populate_signatures('files/bson_files/signatures.bson', 'files/signature_data')
