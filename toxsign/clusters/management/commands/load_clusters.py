from django.core.management.base import BaseCommand, CommandError
from toxsign.users.models import User
from toxsign.clusters.models import Cluster
from django.utils.timezone import now
from datetime import timedelta
from django.core.files import File
import os, sys

def load_clusters(data_folder, distance_type):

    # Start by parsing all three folder to get the correct paths for each cluster

    cluster_dict = _get_cluster_file_paths(data_folder)

    for cluster_id, data in cluster_dict.items():
        _create_cluster(cluster_id, distance_type, data)


def _create_cluster(cluster_id, distance_type, data):

    print("Creating cluster with id {} and type {}".format(cluster_id, distance_type))
    cluster = Cluster(cluster_id=cluster_id, distance_method=distance_type)

    cluster.conditions_file.save("conditions", File(open(data['condition'], "rb")), save=False)

    if 'signature' in data:
        cluster.signature_file.save("signature", File(open(data['signature'], "rb")), save=False)
    if 'chem2enr' in data:
        cluster.chemical_enrichment_file.save("chem2enr", File(open(data['chem2enr'], "rb")), save=False)
    if 'gene2enr' in data:
        cluster.gene_enrichment_file.save("gene2enr", File(open(data['gene2enr'], "rb")), save=False)

    cluster.save()

def _get_cluster_file_paths(data_folder):

    cluster_dict = {}

    for path in os.listdir(os.path.join(data_folder, "Groups")):
        full_path = os.path.join(os.path.join(data_folder, "Groups"), path)
        if os.path.isfile(full_path):
            if not len(path.split(".")) == 3:
                continue
            cluster_id = path.split(".")[1]
            cluster_dict[cluster_id] = {'condition': full_path}

    for path in os.listdir(os.path.join(data_folder, "Signatures")):
        full_path = os.path.join(os.path.join(data_folder, "Signatures"), path)
        if os.path.isfile(full_path) and "GeneIDs" in path:
            if not len(path.split(".")) == 4:
                continue
            cluster_id = path.split(".")[1]
            if not cluster_id in cluster_dict:
                continue
            cluster_dict[cluster_id]['signature'] = full_path

    for path in os.listdir(os.path.join(data_folder, "Enrichissement")):
        full_path = os.path.join(os.path.join(data_folder, "Enrichissement"), path)
        if os.path.isfile(full_path) and ("chem2enr" in path or "gene2enr" in path):
            if not len(path.split(".")) == 4:
                continue
            cluster_id = path.split(".")[1]
            if not cluster_id in cluster_dict or not 'signature' in cluster_dict[cluster_id]:
                continue
            if "chem2enr" in path:
                cluster_dict[cluster_id]['chem2enr'] = full_path
            if "gene2enr" in path:
                cluster_dict[cluster_id]['gene2enr'] = full_path

    return cluster_dict

class Command(BaseCommand):
    help = 'Load clusters from ChemPSy'

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('data_folder', type=str, help='Folder containing the files. Files must be in  Enrichissement, Groups and Signatures folders')
        parser.add_argument('type', type=str, help='Type of distance calculation : correlation or euclidean')

    def handle(self, *args, **options):

        if not options['type'] in ['correlation', 'euclidean']:
            print("Warning : type must be either correlation or euclidean")
            return

        if not os.path.exists(options['data_folder']):
            print("Warning : folder {} does not exists".format(options['data_folder']))
            return

        if not os.path.exists(os.path.join(options['data_folder'], "Enrichissement")) or not os.path.exists(os.path.join(options['data_folder'], "Groups")) or not os.path.exists(os.path.join(options['data_folder'], "Signatures")):
            print("Warning : folder {} does not contain either the Enrichissement, Groups or Signatures folder".format(options['data_folder']))
            return

        load_clusters(options['data_folder'], options['type'])

