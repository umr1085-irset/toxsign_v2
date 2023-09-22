import os
import shutil
import time
import tempfile
from urllib.request import urlopen
from zipfile import ZipFile
import gzip
import subprocess

from toxsign.taskapp.celery import app
from django.conf import settings
from toxsign.genes.models import Gene
from toxsign.jobs.models import Job

@app.task(bind=True)
def prepare_homolog_data(self, force=False):
    urls = [
        "ftp://ftp.ncbi.nih.gov/pub/HomoloGene/current/homologene.data",
        "ftp://ftp.ncbi.nlm.nih.gov/gene/DATA/gene2go.gz",
        "ftp://ftp.geneontology.ORG/pub/go/ontology/gene_ontology.obo",
        "http://purl.obolibrary.org/obo/hp.obo",
        "http://www.informatics.jax.org/downloads/reports/MGI_Gene_Model_Coord.rpt",
        "http://www.informatics.jax.org/downloads/reports/MPheno_OBO.ontology",
        "http://www.informatics.jax.org/downloads/reports/MGI_PhenoGenoMP.rpt"
    ]

    # Should load this from config file maybe
    dest_dir = "/app/toxsign/media/jobs/admin/"
    _download_datafiles(dest_dir, urls, force=force)

    if os.path.exists(os.path.join(dest_dir, "annotation")) and not force:
        print("Annotation file exists, skipping. Use force=True to force the replacement")
        return
    print('Running subprocess')
    run = subprocess.run(['/bin/bash', '/app/tools/prepare_homolog/prepare_homolog.sh'], capture_output=True)
    print(run.stdout.decode())

@app.task(bind=True)
def prepare_cluster_data(self):
    dest_dir = "/app/toxsign/media/jobs/admin/"

    if not os.path.exists(os.path.join(dest_dir, "euclidean_method.RData")):
        print("Building file for euclidean")
        if os.path.exists("/app/loading_data/euclidean_data.reduced.RData") and os.path.exists("/app/toxsign/media/jobs/admin/homologene.data"):
            with tempfile.TemporaryDirectory() as dirpath:
                path_to_groups = "/app/loading_data/ChemPSy/PCA_bin_DynamicCutTree_euclidean/Groups/"
                dest_file = dest_dir + "euclidean_method.RData"
                shutil.copy2("/app/loading_data/euclidean_data.reduced.RData", dirpath + "/data.reduced.RData")
                shutil.copy2("/app/toxsign/media/jobs/admin/homologene.data", dirpath)
                run = subprocess.run(['/bin/bash', '/app/tools/run_cluster_dist/setup_files.sh', path_to_groups, dirpath, dest_file], capture_output=True)
                print(run.stdout.decode())
        else:
            print("Missing either euclidean_method.RData file or homologene file: skipping")

    if not os.path.exists(os.path.join(dest_dir, "correlation_method.RData")):
        print("Building file for correlation")
        if os.path.exists("/app/loading_data/correlation_data.reduced.RData") and os.path.exists("/app/toxsign/media/jobs/admin/homologene.data"):
            with tempfile.TemporaryDirectory() as dirpath:
                path_to_groups = "/app/loading_data/ChemPSy/PCA_bin_DynamicCutTree_correlation/Groups/"
                dest_file = dest_dir + "correlation_method.RData"
                shutil.copy2("/app/loading_data/correlation_data.reduced.RData", dirpath + "/data.reduced.RData")
                shutil.copy2("/app/toxsign/media/jobs/admin/homologene.data", dirpath)
                run = subprocess.run(['/bin/bash', '/app/tools/run_cluster_dist/setup_files.sh', path_to_groups, dirpath, dest_file], capture_output=True)
                print(run.stdout.decode())
        else:
            print("Missing either correlation_method.RData file or homologene file: skipping")

@app.task(bind=True)
def prepare_tools_env(self):
    # Should maybe use a tool parameter (install_script_file?)
    run = subprocess.run(['/bin/bash', '/app/tools/envR_TCL/setupR_TCL'], capture_output=True)
    print(run.stdout.decode())

@app.task(bind=True)
def setup_files(self, signature_id, index_files=False, need_move_files=False):

    from toxsign.signatures.models import Signature
    from .processing import zip_results

    time.sleep(10)
    try:
        signature = Signature.objects.get(id=signature_id)
    except toxsign.signatures.models.DoesNotExist:
        raise Exception("Signature with id {} was not found".format(signature_id))

    new_path = "files/{}/{}/{}/{}/".format(signature.factor.assay.project.tsx_id, signature.factor.assay.tsx_id, signature.factor.tsx_id, signature.tsx_id)
    new_unix_path = settings.MEDIA_ROOT + "/" + new_path
    if not os.path.exists(new_unix_path):
        os.makedirs(new_unix_path)

    if index_files:
        signature = index_genes(signature, new_path, new_unix_path)

    if need_move_files:
        signature = move_files(signature, new_path, new_unix_path)

    signature.save()

    zip_results(new_unix_path)

    if index_files and signature.factor.assay.project.status == "PUBLIC":
        change_status.delay(signature.factor.assay.project.id)

def index_genes(signature, new_path, new_unix_path):

    shutil.move(signature.up_gene_file_path.path, new_unix_path + "up_genes.txt")
    shutil.move(signature.down_gene_file_path.path, new_unix_path + "down_genes.txt")
    shutil.move(signature.interrogated_gene_file_path.path, new_unix_path + "all_genes.txt")

    signature.up_gene_file_path.name = new_path + "up_genes.txt"
    signature.down_gene_file_path.name = new_path + "down_genes.txt"
    signature.interrogated_gene_file_path.name = new_path + "all_genes.txt"

    gene_dict, count = _generate_values(signature)
    signature.expression_values = _format_values(gene_dict)
    _write_gene_file(gene_dict, new_unix_path + signature.tsx_id + ".sign")
    signature.expression_values_file.name = new_path + signature.tsx_id + ".sign"

    signature.up_gene_number = count['up']
    signature.down_gene_number = count['down']
    signature.interrogated_gene_number = count['all']

    return signature

def move_files(signature, new_path, new_unix_path):

    shutil.move(signature.additional_file_path.path, new_unix_path + "additional.txt")
    signature.additional_file_path.name = new_path + "additional.txt"
    return signature

@app.task(bind=True)
def change_status(self, project_id=None):
    # Import here to avoid cyclical import
    from toxsign.projects.models import Project
    from toxsign.signatures.models import Signature
    # M.B 15/02/23: Disable matrix computation
    return

    temp_dir_path = "/app/toxsign/media/jobs/temp/" + self.request.id + "/"

    if os.path.exists(temp_dir_path):
        print("Folder {} already exists: stopping..".format(temp_dir_path))
        return

    # Should test if this project has signature. No point in recalculating if nothing is new
    if project_id:
        project_sig = Signature.objects.filter(factor__assay__project__id=project_id)
        if not project_sig.exists():
            return

    public_sigs = Signature.objects.filter(factor__assay__project__status="PUBLIC")
    if not public_sigs.exists():
        return

    os.mkdir(temp_dir_path)

    for sig in public_sigs:
        if sig.expression_values_file and os.path.exists(sig.expression_values_file.path):
            shutil.copy2(sig.expression_values_file.path, temp_dir_path)
    if os.path.exists("/app/toxsign/media/jobs/admin/public.RData"):
        shutil.copy2("/app/toxsign/media/jobs/admin/public.RData", temp_dir_path + "public.RData.old")

    # Need to check the result...
    subprocess.run(['/bin/bash', '/app/tools/make_public/make_public.sh', temp_dir_path])


@app.task(bind=True)
def setup_cluster(self, cluster_id):

    from toxsign.clusters.models import Cluster
    # Make sure the entity is saved before anything
    time.sleep(10)
    try:
        cluster = Cluster.objects.get(id=cluster_id)
    except toxsign.signatures.models.DoesNotExist:
        raise Exception("Cluster with id {} was not found".format(cluster_id))

    if cluster.conditions_file:
        cluster.conditions = _process_cluster_conditions(cluster.conditions_file)
    if cluster.signature_file:
        cluster.signature = _process_cluster_signature(cluster.signature_file)

    cluster.save()


def _process_cluster_conditions(condition_file):

    if not condition_file or not os.path.exists(condition_file.path):
        return {'unique_chemicals': 0, 'conditions': []}

    chemicals = set()
    conditions = []
    with open(condition_file.path, 'r') as f:
        for line in f:
            data = _process_condition_line(line)
            if not data:
                continue
            chemicals.add(data['chemical'])
            conditions.append(data)
    results = {'unique_chemicals': len(chemicals), 'conditions': conditions}

    return results

def _process_condition_line(line):

    data = {}

    line_values = line.split("+")
    if not len(line_values) == 6:
        return {}

    data['geo_id'] = line_values[0]
    data['tissue'] = line_values[1].title()
    data['chemical'] = line_values[2].title()
    data['generation'] = line_values[3]
    data['concentration'] = _process_data(line_values[4])
    data['exposure'] = _process_data(line_values[5])

    return data

def _process_data(data):

    if not data:
        return "NA"

    return " ".join(data.split("_"))

def _process_cluster_signature(signature_file):

    if not signature_file or not os.path.exists(signature_file.path):
        return {}

    gene_list = []

    with open(signature_file.path, 'r') as f:
        for line in f:
            data = {"gene_id" : line.rstrip()}
            gene = Gene.objects.filter(gene_id=line.rstrip())
            if gene.count():
                gene = gene[0]
                data = {"gene_id" : gene.gene_id, "symbol": gene.symbol}
            else:
                data = {"gene_id" : line.rstrip(), "symbol": "NA"}
            gene_list.append(data)
    return {"gene_list": gene_list}

def _generate_values(signature):
    # Starts from scratch
    values = {}
    count = {
        'up': 0,
        'down': 0,
        'all': 0
    }
    gene_type = signature.gene_id
    # Starts with interrogated file to get them all (we will upload them later)
    if signature.interrogated_gene_file_path:
        values, count['all'] = _prepare_values(values, signature.interrogated_gene_file_path.path, gene_type)
    if signature.up_gene_file_path:
        values, count['up'] = _extract_values(values, signature.up_gene_file_path.path, gene_type, "1")
    if signature.down_gene_file_path:
        values, count['down'] = _extract_values(values, signature.down_gene_file_path.path, gene_type, "-1")
    return values, count

def _extract_values(values, file, gene_type, expression_value=None):

    count = 0
    if not os.path.exists(file):
        return values, count

    with open(file, 'r') as f:
        for line in f:
            gene_id = line.split("\t")[0].strip()
            if not gene_id:
                continue
            count += 1
            # Shoud not happen, but just in case
            if not gene_id in values:
                values[gene_id] = {'value': expression_value, 'homolog_id': 'NA', 'gene_name':"NA", 'in_base': 0}
            else:
                values[gene_id]['value'] = expression_value

    return values, count

def _prepare_values(values, file, gene_type):

    genes = set()
    processed_genes = set()

    if not os.path.exists(file):
        return values, 0

    with open(file, 'r') as f:
        for line in f:
            gene_id = line.split("\t")[0].strip()
            if gene_id:
                genes.add(gene_id)

    if gene_type == "ENTREZ":
        for gene in Gene.objects.filter(gene_id__in=genes).values('gene_id', 'homolog_id', 'symbol'):
            processed_genes.add(gene['gene_id'])
            values[gene['gene_id']] = {'value': 0, 'homolog_id': gene['homolog_id'], 'gene_name': gene['symbol'], 'in_base': 1}
        for missing_gene in genes - processed_genes:
            values[missing_gene] = {'value': 0, 'homolog_id': 'NA', 'gene_name':"NA", 'in_base': 0}

    else:
        for gene in Gene.objects.filter(ensembl_id__in=genes).values('ensembl_id', 'homolog_id', 'symbol'):
            processed_genes.add(gene['ensembl_id'])
            values[gene['ensembl_id']] = {'value': 0, 'homolog_id': gene['homolog_id'], 'gene_name': gene['symbol'], 'in_base': 1}
        for missing_gene in genes - processed_genes:
            values[missing_gene] = {'value': 0, 'homolog_id': 'NA', 'gene_name':"NA", 'in_base': 0}

    return values, len(genes)

def _write_gene_file(gene_values, path):

    file = open(path, "w")
    for key, value in gene_values.items():
        file.write("{}\t{}\t{}\t{}\t{}\n".format(key, value["gene_name"], value["homolog_id"], value["in_base"], value["value"]))
    file.close()

def _format_values(gene_values):
    val = {'up_genes': [], 'down_genes': []}

    for key, value in gene_values.items():
        if value["value"] == "1":
            val['up_genes'].append(key)
        elif value["value"] == "-1":
            val['down_genes'].append(key)
    return val

def _download_datafiles(dest_dir, url_list, force=False):

    for url in url_list:
        file_name =  url.split('/')[-1]
        # Do not re-download if not needed and not forced
        if os.path.exists(os.path.join(dest_dir, file_name.replace('.gz',''))) and not force:
            print(file_name + " exists, skipping download. Use force=True to force the replacement")
            continue
        f = open(os.path.join(dest_dir, file_name), 'wb')
        u = urlopen(url)
        meta = u.info()
        file_size = int(meta.get("Content-Length")[0])
        print("Downloading: %s"% (file_name))
        file_size_dl = 0
        block_sz = 8192
        while True:
            buffer = u.read(block_sz)
            if not buffer:
                break
            file_size_dl += len(buffer)
            f.write(buffer)
        f.close()
        if ".gz" in file_name:
            with gzip.open(os.path.join(dest_dir, file_name), 'rb') as f_in:
                with open(os.path.join(dest_dir, file_name.replace('.gz','')), 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)


