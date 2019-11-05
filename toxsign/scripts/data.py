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
    dest_dir = "/app/tools/admin_data/"
    _download_datafiles(dest_dir, urls, force=force)

    if os.path.exists(os.path.join(dest_dir, "annotation")) and not force:
        print("Annotation file exists, skipping. Use force=True to force the replacement")
        return
    print('Running subprocess')
    run = subprocess.run(['/bin/bash', '/app/tools/prepare_homolog/prepare_homolog.sh'], capture_output=True)
    print(run.stdout.decode())

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
    signature = Signature.objects.get(id=signature_id)

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
    shutil.move(signature.expression_values_file.path, new_unix_path + signature.tsx_id + ".sign")

    signature.up_gene_file_path.name = new_path + "up_genes.txt"
    signature.down_gene_file_path.name = new_path + "down_genes.txt"
    signature.interrogated_gene_file_path.name = new_path + "all_genes.txt"

    gene_dict = _generate_values(signature)
    signature.expression_values = gene_dict
    _write_gene_file(gene_dict, new_unix_path + signature.tsx_id + ".sign")
    signature.expression_values_file.name = new_path + signature.tsx_id + ".sign"

    signature.up_gene_number = _count_lines(new_unix_path + "up_genes.txt")
    signature.down_gene_number = _count_lines(new_unix_path + "down_genes.txt")
    signature.interrogated_gene_number = _count_lines(new_unix_path + "all_genes.txt")

    return signature

def move_files(signature, new_path, new_unix_path):

    shutil.move(signature.additional_file_path.path, new_unix_path + "additional.txt")
    signature.additional_file_path.name = new_path + "additional.txt"
    return signature

@app.task(bind=True)
def change_status(self, project_id):
    # Import here to avoid cyclical import
    from toxsign.projects.models import Project
    from toxsign.signatures.models import Signature
    temp_dir_path = "/app/tools/job_dir/temp/" + self.request.id + "/"

    if os.path.exists(temp_dir_path):
        print("Folder {} already exists: stopping..".format(temp_dir_path))
        return

    # Should test if this project has signature. No point in recalculating if nothing is new
    project_sig = Signature.objects.filter(factor__assay__project__id=project_id)
    if not project_sig.exists():
        return

    public_sigs = Signature.objects.filter(factor__assay__project__status="PUBLIC")
    if not public_sigs.exists():
        return

    os.mkdir(temp_dir_path)

    for sig in public_sigs:
        if sig.expression_values_file:
            shutil.copy2(sig.expression_values_file.path, temp_dir_path)
    if os.path.exists("/app/tools/admin_data/public.RData"):
        shutil.copy2("/app/tools/admin_data/public.RData", temp_dir_path + "public.RData.old")

    # Need to check the result...
    subprocess.run(['/bin/bash', '/app/tools/make_public/make_public.sh', temp_dir_path])


def _count_lines(path):
    with open(path) as f:
        for i, l in enumerate(f):
            pass
    return i + 1

def _generate_values(signature):
    # Starts from scratch
    values = {}
    gene_type = signature.gene_id
    # Starts with interrogated file to get them all (we will upload them later)
    if signature.interrogated_gene_file_path:
        values = _prepare_values(values, signature.interrogated_gene_file_path.path, gene_type)
    if signature.up_gene_file_path:
        values = _extract_values(values, signature.up_gene_file_path.path, gene_type, "1")
    if signature.down_gene_file_path:
        values = _extract_values(values, signature.down_gene_file_path.path, gene_type, "-1")
    return values

def _extract_values(values, file, gene_type, expression_value=None):

    genes = set()
    if not os.path.exists(file):
        return values
    with open(file, 'r') as f:
        for line in f:
            gene_id = line.strip()
            # Shoud not happen, but just in case
            if not gene_id in values:
                values[gene_id] = {'value': expression_value, 'homolog_id': 'NA', 'gene_name':"NA", 'in_base': 0}
            else:
                values[gene_id]['value'] = expression_value

    return values

def _prepare_values(values, file, gene_type):

    genes = set()
    processed_genes = set()

    if not os.path.exists(file):
        return values

    with open(file, 'r') as f:
        for line in f:
            gene_id = line.strip()
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

    return values

def _write_gene_file(gene_values, path):

    file = open(path, "w")
    for key, value in gene_values.items():
        file.write("{}\t{}\t{}\t{}\t{}\n".format(key, value["gene_name"], value["homolog_id"], value["in_base"], value["value"]))
    file.close()


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
