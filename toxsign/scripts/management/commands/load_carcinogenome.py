import json, os
from django.conf import settings
from django.db import migrations
from django.apps import apps
from django.core.management.base import BaseCommand, CommandError
from django.core.files import File
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist

from toxsign.superprojects.models import *
from toxsign.projects.models import Project
from toxsign.assays.models import *
from toxsign.signatures.models import *
from toxsign.users.models import User
from toxsign.ontologies.models import *

from toxsign.scripts.data import change_status

User = get_user_model()

def import_superproject(dict_superproject,user,key):
    """
        Import surper project
        dict_superproject : dictionnary
        user : django user object
    """
    dict_to_insert = {}
    if not Superproject.objects.filter(name = dict_superproject[key]['name']).exists() :
        # Manually mapping each keys thank you Indusha ^^
        dict_to_insert['name'] = dict_superproject[key]['name']
        dict_to_insert['contact_mail'] = dict_superproject[key]['contact_mail']
        dict_to_insert['description'] = dict_superproject[key]['description']
        dict_to_insert['created_by'] = user

        # Create SuperProject from dict_to_insert
        sp = Superproject.objects.create(**dict_to_insert)
        sp.save()

        # Get SuperProject ID and return data dict 
    else :
        print("SuperProject exists")
        
def import_project(dict,user,key):
    dict_to_insert =  {}
    super_project = Superproject.objects.get(name=dict["superproject"]['name'])
    if not Project.objects.filter(name = dict[key]['name']).exists() :
        # Manually mapping each keys thank you Indusha ^^ (again)
        dict_to_insert['name'] = dict[key]['name']
        dict_to_insert['description'] = dict[key]['description']
        dict_to_insert['created_by'] = user

        # Add genotox & carcinotox information in description
        if dict[key]['carcinogenicity_liver'] != "NA" :
            dict_to_insert['description'] = dict_to_insert['description'] + '\n Liver Carcinogenicity'+ dict[key]['carcinogenicity_liver']
        if dict[key]['genotoxicity_liver'] != "NA" :
            dict_to_insert['description'] = dict_to_insert['description'] + '\n Liver Genotoxicity'+ dict[key]['genotoxicity_liver']
        if dict[key]['carcinogenicity_breast'] != "NA" :
            dict_to_insert['description'] = dict_to_insert['description'] + '\n Breast Carcinogenicity'+ dict[key]['carcinogenicity_breast']
        if dict[key]['genotoxicity_breast'] != "NA" :
            dict_to_insert['description'] = dict_to_insert['description'] + '\n Breast Genotoxicity'+ dict[key]['genotoxicity_breast']
        dict_to_insert['project_type'] = dict[key]['project_type']
        dict_to_insert['status'] = "PRIVATE"
        p=Project.objects.create(**dict_to_insert)
        p.superproject = super_project
        p.save()
    else :
        print("Project exists")


def import_assay(dict,user,key):
    dict_to_insert =  {}
    if not Assay.objects.filter(name = dict[key]['name']).exists() :
        # Manually mapping each keys thank you Indusha ^^ (again)
        print("insert assay " + dict[key]['name'])
        dict_to_insert =  {}
        dict_to_insert['name'] = dict[key]['name']
        dict_to_insert['description'] = dict[key]['description']
        dict_to_insert['created_by'] = user
        dict_to_insert['experimental_design'] = dict[key]['experimental_design']
        dict_to_insert['additional_info'] = dict[key]['additional_information']
        dict_to_insert['dev_stage'] = dict[key]['dev_stage']
        dict_to_insert['generation'] = dict[key]['generation']
        dict_to_insert['sex_type'] = dict[key]['sex_type']
        dict_to_insert['exp_type'] = dict[key]['exp_type']

        if dict[key]['organism'] != '':
            dict_to_insert['organism'] = Species.objects.get(name=dict[key]['organism'])
        if dict[key]['tissue'] != '':
            dict_to_insert['tissue'] = Tissue.objects.get(name=dict[key]['tissue'])
        if dict[key]['cell'] != '':
            if dict[key]['cell'] == "epithelial" :
                dict[key]['cell'] = "epithelial cell"
            dict_to_insert['cell'] = Cell.objects.get(name=dict[key]['cell'])
        if dict[key]['cell_line'] != '':
            if dict[key]['cell_line'] == "breast fybrocystic disease" :
                dict[key]['cell_line'] = "breast fibrocystic disease"
            dict_to_insert['cell_line'] = CellLine.objects.get(name=dict[key]['cell_line'])

        dict_to_insert['cell_line_slug'] = dict[key]['cell_line_slug']
        dict_to_insert['results'] = dict[key]['results']

        project = Project.objects.get(name=dict["project"]["name"])
        a=Assay.objects.create(**dict_to_insert)
        a.project = project
        a.save()
    else :
        print("Assay exists")    

def import_factor(dict,user,key):
    dict_to_insert =  {}
    if not Factor.objects.filter(name = dict[key]['name']).exists() :

        # Manually mapping each keys thank you Indusha ^^ (again)
        dict_to_insert =  {}
        dict_to_insert['name'] = dict[key]['name']
        dict_to_insert['created_by'] = user

        assay = Assay.objects.get(name=dict["assay"]["name"])
        f=Factor.objects.create(**dict_to_insert)
        f.assay = assay
        f.save()

        key = "subfactor"
        dict_to_insert =  {}
        dict_to_insert['created_by'] = user

        chemical_slug = dict[key]['chemical_slug']

        if dict[key]['chebi_id'] != '':
            try:
                chemical = Chemical.objects.get(onto_id="CHEBI:" + dict[key]['chebi_id'])
                dict_to_insert['chemical'] = chemical

            except ObjectDoesNotExist:
                if not chemical_slug:
                    chemical_slug = dict[key]['chemical']

        dict_to_insert['route'] = dict[key]['route']
        dict_to_insert['vehicule'] = dict[key]['vehicule']
        dict_to_insert['chemical_slug'] = chemical_slug

        if " " in dict[key]['dose_value']:
            dose_value = float(dict[key]['dose_value'].split(" ")[0])
            dose_unit = "nM"
        else:
            dose_value = float(dict[key]['dose_value'])
            dose_unit = "µM"

        dict_to_insert['dose_value'] = dose_value
        dict_to_insert['dose_unit'] = dose_unit

        dict_to_insert['exposure_time'] = float(dict[key]['exposure_time'])
        dict_to_insert['exposure_frequencie'] = dict[key]['exposure_frequencie']
        dict_to_insert['factor'] = f
        sf=ChemicalsubFactor.objects.create(**dict_to_insert)
        sf.save()
    else :
        print("Factor exists")
    return dict            


def import_signature(dict,user,key):
    dict_to_insert =  {}
    signatures_file_dir = "loading_data/carcinogenome/6_signature/sig_files"
    if not Signature.objects.filter(name = dict[key]['name']).exists() :
    # Manually mapping each keys thank you Indusha ^^ (again)
        dict_to_insert['created_by'] = user
        dict_to_insert['name'] = dict[key]['name']
        dict_to_insert['signature_type'] = "GENOMICS"
        dict_to_insert['phenotype_description'] = dict[key]['phenotype_description']
        dict_to_insert['experimental_design'] = dict[key]['experimental_design']
        dict_to_insert['dev_stage'] = dict[key]['dev_stage']
        dict_to_insert['generation'] = dict[key]['generation']
        dict_to_insert['sex_type'] = dict[key]['sex_type']
        dict_to_insert['exp_type'] = dict[key]['exp_type']

        if dict[key]['organism'] != '':
            dict_to_insert['organism'] = Species.objects.get(name=dict[key]['organism'])
        if dict[key]['tissue'] != '':
            dict_to_insert['tissue'] = Tissue.objects.get(name=dict[key]['tissue'])
        if dict[key]['cell'] != '':
            dict_to_insert['cell'] = Cell.objects.get(name=dict[key]['cell'])
        if dict[key]['cell_line'] != '':
            dict_to_insert['cell_line'] = CellLine.objects.get(name=dict[key]['cell_line'])

        chemical_slug = dict[key]['chemical_slug']

        if dict[key]['chebi_id'] != '':
            try:
                chemical = Chemical.objects.get(onto_id="CHEBI:" + dict[key]['chebi_id'])
                dict_to_insert['chemical'] = chemical

            except ObjectDoesNotExist:
                if not chemical_slug:
                    chemical_slug = dict[key]['chemical']

        dict_to_insert['chemical_slug'] = chemical_slug
        dict_to_insert['technology_slug'] = dict[key]['technology_slug']
        dict_to_insert['platform'] = dict[key]['plateform']
        if dict[key]['control_sample_number'] == '' :
            dict_to_insert['control_sample_number'] = None
        else :
            dict_to_insert['control_sample_number'] = dict[key]['control_sample_number']
        
        if dict[key]['treated_sample_number'] == '' :
            dict_to_insert['treated_sample_number'] = None
        else :
            dict_to_insert['treated_sample_number'] = dict[key]['treated_sample_number']
        dict_to_insert['pvalue'] = float(dict[key]['pvalue'])
        dict_to_insert['cutoff'] = float(dict[key]['cutoff'])
        dict_to_insert['statistical_processing'] = dict[key]['statistical_processing']
        dict_to_insert['gene_id'] = "ENTREZ"

        factor = Factor.objects.get(name=dict["factor"]['name'])
        s=Signature.objects.create(**dict_to_insert)
        s.factor = factor
        s.save()

        #dict_to_insert['down_gene_file_path'] = File(open(os.path.join(settings.ROOT_DIR,signatures_file_dir,"DOWN",dict[key]['down_gene_file_path'])))
        #dict_to_insert['up_gene_file_path']= File(open(os.path.join(settings.ROOT_DIR,signatures_file_dir,"UP",dict[key]['up_gene_file_path'])))
        #dict_to_insert['interrogated_gene_file_path']= File(open(os.path.join(settings.ROOT_DIR,signatures_file_dir,"ALL",dict[key]['interrogated_gene_file_path'].replace('_signature.txt','_all.txt'))))
        #dict_to_insert['additional_file_path']= File(open(os.path.join(settings.ROOT_DIR,signatures_file_dir,"ADDITIONAL",dict[key]['interrogated_gene_file_path'].replace('_signature.txt','_all.txt'))))

        s.up_gene_file_path.save(dict[key]['up_gene_file_path'], File(open(os.path.join(settings.ROOT_DIR,signatures_file_dir,"UP",dict[key]['up_gene_file_path']))), save=False)
        s.down_gene_file_path.save(dict[key]['down_gene_file_path'], File(open(os.path.join(settings.ROOT_DIR,signatures_file_dir,"DOWN",dict[key]['down_gene_file_path']))), save=False)
        s.interrogated_gene_file_path.save(dict[key]['interrogated_gene_file_path'].replace('_signature.txt','_all.txt'), File(open(os.path.join(settings.ROOT_DIR,signatures_file_dir,"ALL",dict[key]['interrogated_gene_file_path'].replace('_signature.txt','_all.txt')))), save=False)

        if os.path.exists(os.path.join(settings.ROOT_DIR,signatures_file_dir,"ADDITIONAL",dict[key]['interrogated_gene_file_path'].replace('_signature.txt','_zscore.txt'))):
            s.additional_file_path.save(dict[key]['interrogated_gene_file_path'], File(open(os.path.join(settings.ROOT_DIR,signatures_file_dir,"ADDITIONAL",dict[key]['interrogated_gene_file_path'].replace('_signature.txt','_zscore.txt')))), save=False)

        s.save(force=True)
    else :
        print('Signature exists')

def publicize_project(project_dict):
    project = Project.objects.get(name=project_dict['name'])
    project.status = "PRIVATE"
    project.save(force=True)

def import_data_from_list(signaturefile):
    f = open(signaturefile,)

    # returns JSON object as
    # a dictionary
    json_file = json.load(f)

    admin_user = User.objects.filter(is_superuser=True)
    if not admin_user:
        print("No superuser created, aborting")
    else:
        admin_user = admin_user[0]

    #for sign_obj in json_file :
    #    print("Running import Superproject")
    #    import_superproject(sign_obj,admin_user,'superproject')

    #    print("Running import project")
    #    import_project(sign_obj,admin_user,'project')

    #    print("Running import assays")
    #    import_assay(sign_obj,admin_user,'assay')

    #    print("Running import factor")
    #    import_factor(sign_obj,admin_user,'factor')

    #    print("Running import signature")
    #    import_signature(sign_obj,admin_user,'signatures')


    # We should actually publicize projects (and run change_status) only once all signatures are integrated 

    #for sign_obj in json_file :
        #publicize_project(sign_obj['project'])

    #change_status.delay()


def launch_import(signature_data_folder) :
    import_data_from_list(signature_data_folder)

class Command(BaseCommand):

    help = 'Load signatures'

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('signature_data_folder', type=str, help='Folder containing the signature data (TSPX, etc...)')

    def handle(self, *args, **options):
        launch_import(options['signature_data_folder'])
