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

@app.task
def setup_tools_env():
    # Should maybe use a tool parameter (install_script_file?)
    run = subprocess.run(['/bin/bash', '/app/tools/envR_TCL/setupR_TCL'], capture_output=True)
    print(run.stdout.decode())

@app.task
def setup_homolog_data(force=False):
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

    if os.path.exists(os.path.join(dest_dir, "annotation")) and not True:
        print("Annotation file exists, skipping. Use force=True to force the replacement")
        return
    print('Running subprocess')
    run = subprocess.run(['/bin/bash', '/app/tools/prepare_homolog/prepare_homolog.sh'], capture_output=True)
    print(run.stdout.decode())


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
