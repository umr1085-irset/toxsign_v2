import json, os

from django.db import migrations
from django.apps import apps
from django.core.management.base import BaseCommand, CommandError

from toxsign.superprojects.models import *
from toxsign.projects.models import *
from toxsign.assays.models import *
from toxsign.signatures.models import *
from toxsign.users.models import *
from toxsign.ontologies.models import *

def import_superproject(directory,dict,useremail):
    super_projects = os.listdir(directory)
    user = User.objects.get(email=useremail)
    for super_project in super_projects :
        dict_to_insert = {}
        super_project_json = json.loads(os.path.join(directory,super_project))

        # Manually mapping each keys thank you Indusha ^^
        dict_to_insert['name'] = super_project_json['Name']
        dict_to_insert['contact_mail'] = super_project_json['Contact mail']
        dict_to_insert['description'] = super_project_json['Description']
        dict_to_insert['created_by'] = user

        # Create SuperProject from dict_to_insert
        sp = Superproject.objects.create(**dict_to_insert)
        sp.save()

        # Get SuperProject ID and return data dict 
        dict["super_project"] = sp.id
        
    return dict

def import_project(directory,dict,useremail):
    projects = os.listdir(directory)
    user = User.objects.get(email=useremail)
    super_project = Superproject.objects.get(id=dict["super_project"])
    for project in projects :
        project_json = json.loads(os.path.join(directory,project))

        for key in project_json :
            if key not in dict :
                dict[key]=dict()

            # Manually mapping each keys thank you Indusha ^^ (again)
            dict_to_insert =  {}
            dict_to_insert['name'] = project_json[key]['Name']
            dict_to_insert['description'] = project_json[key]['Description']
            dict_to_insert['created_by'] = user

            # Add genotox & carcinotox information in description
            if project_json['Carcinogenicity'] != "NA" :
                dict_to_insert['description'] = dict_to_insert['description'] + '\n'+ project_json[key]['Carcinogenicity']
            if project_json['Genotoxicity'] != "NA" :
                dict_to_insert['description'] = dict_to_insert['description'] + '\n'+ project_json[key]['Genotoxicity']
            dict_to_insert['project_type'] = project_json[key]['Project type']

            p=Project.objects.create(**dict_to_insert)
            p.superproject = super_project
            p.save()
            dict[key]["project"] = p.id
    return dict

def import_assay(directory,dict,useremail):
    assays = os.listdir(directory)
    user = User.objects.get(email=useremail)
    for assay in assays :
        assays_json = json.loads(os.path.join(directory,assay))
        for key in assays_json :
            if key not in dict :
                dict[key]=dict()

            # Manually mapping each keys thank you Indusha ^^ (again)
            dict_to_insert =  {}
            dict_to_insert['name'] = assays_json[key]['Name']
            dict_to_insert['description'] = assays_json[key]['Description']
            dict_to_insert['created_by'] = user
            dict_to_insert['experimental_design'] = assays_json[key]['Experimental design']
            dict_to_insert['additional_info'] = assays_json[key]['Additional information']
            dict_to_insert['dev_stage'] = assays_json[key]['Dev stage']
            dict_to_insert['generation'] = assays_json[key]['Generation']
            dict_to_insert['sex_type'] = assays_json[key]['Sex type']
            dict_to_insert['exp_type'] = assays_json[key]['Exp type']

            if assays_json[key]['Organism'] != '':
                dict_to_insert['organism'] = Species.objects.get(name=assays_json[key]['Organism'])
            if assays_json[key]['Tissue'] != '':
                dict_to_insert['tissue'] = Tissue.objects.get(name=assays_json[key]['Tissue'])
            if assays_json[key]['Cell'] != '':
                dict_to_insert['cell'] = Cell.objects.get(name=assays_json[key]['Cell'])
            if assays_json[key]['Cell line'] != '':
                dict_to_insert['cell_line'] = CellLine.objects.get(name=assays_json[key]['Cell line'])

            dict_to_insert['cell_line_slug'] = assays_json[key]['Cell line slug']
            dict_to_insert['results'] = assays_json[key]['Results']

            project = Project.objects.get(id=dict[key]["project"])
            a=Assay.objects.create(**dict_to_insert)
            a.project = project
            a.save()
            dict[key]["assay"] = a.id
    return dict            

def import_factor(directory,dict,useremail):
    factors = os.listdir(directory)
    user = User.objects.get(email=useremail)
    for factor in factors :
        factors_json = json.loads(os.path.join(directory,factor))
        for key in factors_json :
            if key not in dict :
                dict[key]=dict()

            # Manually mapping each keys thank you Indusha ^^ (again)
            dict_to_insert =  {}
            dict_to_insert['name'] = factors_json[key]['Name']
            dict_to_insert['created_by'] = user

            assay = Assay.objects.get(id=dict[key]["assay"])
            f=Factor.objects.create(**dict_to_insert)
            f.assay = assay
            f.save()
            dict[key]["factor"] = f.id
    return dict            

def import_subfactor(directory,dict,useremail):
    sub_factors = os.listdir(directory)
    user = User.objects.get(email=useremail)
    for sub_factor in sub_factors :
        sub_factors_json = json.loads(os.path.join(directory,sub_factor))
        for key in sub_factors_json :
            if key not in dict :
                dict[key]=dict()
            
            # Manually mapping each keys thank you Indusha ^^ (again)
            dict_to_insert =  {}
            dict_to_insert['created_by'] = user
            if sub_factors_json[key]['Chemical'] != '':
                dict_to_insert['chemical'] = Chemical.objects.get(name=sub_factors_json[key]['Chemical'])
            dict_to_insert['route'] = sub_factors_json[key]['Route']
            dict_to_insert['vehicule'] = sub_factors_json[key]['Vehicule']
            dict_to_insert['dose_value'] = sub_factors_json[key]['Dose value']
            dict_to_insert['dose_unit'] = sub_factors_json[key]['Dose unit']
            dict_to_insert['exposure_time'] = sub_factors_json[key]['Exposure time']
            dict_to_insert['exposure_frequencie'] = sub_factors_json[key]['Exposure frequencie']
            dict_to_insert['chemical_slug'] = sub_factors_json[key]['Chemical slug']

            factor = Factor.objects.get(id=dict[key]["factor"])
            sf=ChemicalsubFactor.objects.create(**dict_to_insert)
            sf.factor = factor
            sf.save()
            dict[key]["subfactor"] = sf.id
    return dict

########################################
# WIP
#######################################
def import_signature(directory,dict,useremail):
    signatures = os.listdir(directory)
    signatures_file_dir = os.path.join(directory,"sig_files")
    user = User.objects.get(email=useremail)
    for signature in signatures :
        signatures_json = json.loads(os.path.join(directory,signature))
        for key in signatures_json :
            if key not in dict :
                dict[key]=dict()
            signatures_json['']
            factor = Factor.objects.get(id=dict[key]["factor"])
            s=Signature.objects.create(**signatures_json[key])
            s.factor = factor
            s.save()
            dict[key]["signature"] = s.id
    return dict            



def launch_import(signature_data_folder,admin_mail,admin_password) :
    print('Start import signatures')
    dir_list = [
        "1_superproject",
        "2_project",
        "3_assay",
        "4_factor",
        "5_subfactor",
        "6_signature",
        "7_sig_files"
    ]
    dict_data = dict()


class Command(BaseCommand):

    help = 'Load signatures'

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('signature_data_folder', type=str, help='Folder containing the signature data (TSPX, etc...)')
        parser.add_argument('admin_mail', type=str, help='Admin mail adress')
        parser.add_argument('admin_password', type=str, help='Admin password')

    def handle(self, *args, **options):
        launch_import(options['signature_data_folder'], options['admin_mail'], options['admin_password'])