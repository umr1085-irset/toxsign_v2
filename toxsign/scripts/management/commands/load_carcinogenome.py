import json, os

from django.db import migrations
from django.apps import apps
from django.core.management.base import BaseCommand, CommandError

from toxsign.superprojects.models import *
from toxsign.projects.models import *
from toxsign.assays.models import *
from toxsign.signatures.models import *
from toxsign.users.models import *

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
            dict_to_insert['name'] = project_json['Name']
            dict_to_insert['description'] = project_json['Description']
            dict_to_insert['created_by'] = user

            # Add genotox & carcinotox information in description
            if project_json['Carcinogenicity'] != "NA" :
                dict_to_insert['description'] = dict_to_insert['description'] + '\n'+ project_json['Carcinogenicity']
            if project_json['Genotoxicity'] != "NA" :
                dict_to_insert['description'] = dict_to_insert['description'] + '\n'+ project_json['Genotoxicity']
            dict_to_insert['project_type'] = project_json['Project type']

            p=Project.objects.create(**project_json[key])
            p.superproject = super_project
            p.save()
            dict[key]["project"] = p.id
    return dict

#########################################
#  WIP 
#########################################
def import_assay(directory,dict):
    assays = os.listdir(directory)
    for assay in assays :
        assays_json = json.loads(os.path.join(directory,assay))
        for key in assays_json :
            if key not in dict :
                dict[key]=dict()
            project = Project.objects.get(id=dict[key]["project"])
            a=Assay.objects.create(**assays_json[key])
            a.project = project
            a.save()
            dict[key]["assay"] = a.id
    return dict            

def import_factor(directory,dict):
    factors = os.listdir(directory)
    for factor in factors :
        factors_json = json.loads(os.path.join(directory,factor))
        for key in factors_json :
            if key not in dict :
                dict[key]=dict()
            assay = Assay.objects.get(id=dict[key]["assay"])
            f=Factor.objects.create(**factors_json[key])
            f.assay = assay
            f.save()
            dict[key]["factor"] = f.id
    return dict            

def import_subfactor(directory,dict):
    sub_factors = os.listdir(directory)
    for sub_factor in sub_factors :
        sub_factors_json = json.loads(os.path.join(directory,sub_factor))
        for key in sub_factors_json :
            if key not in dict :
                dict[key]=dict()
            factor = Factor.objects.get(id=dict[key]["factor"])
            sf=ChemicalsubFactor.objects.create(**sub_factors_json[key])
            sf.factor = factor
            sf.save()
            dict[key]["subfactor"] = sf.id
    return dict

def import_signature(directory,dict):
    signatures = os.listdir(directory)
    signatures_file_dir = os.path.join(directory,"sig_files")
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