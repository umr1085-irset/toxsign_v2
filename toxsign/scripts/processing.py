import os
import shutil
import time
import tempfile
from urllib.request import urlopen
from zipfile import ZipFile
import gzip
import subprocess
import datetime
import time

from toxsign.taskapp.celery import app

from toxsign.projects.views import check_view_permissions
from toxsign.projects.models import Project
from toxsign.signatures.models import Signature

from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

class TaskFailure(Exception):
   pass

#@app.task(bind=True)
def run_distance(signature_id, user_id=None):

    dt = datetime.datetime.utcnow()
    ztime = time.mktime(dt.timetuple())
#    task_id = self.request.id + "_" + str(ztime)
    task_id = "156446546" + "_" + str(ztime)

    # Does it work with no rData file? Using only provided signatures?
    if not os.path.exists("/app/tools/admin_data/public.RData"):
        logger.exception("No public.RData file. Stopping..")
        raise TaskFailure('No public.RData file')

    job_dir_path = "/app/tools/job_dir/results/" + task_id + "/"

    if os.path.exists(job_dir_path):
        logger.exception("Result directory {} already exists. Stopping.".format(task_id))
        raise TaskFailure('Result directory already exists')

    os.mkdir(job_dir_path)

    # If is logged, get all available (private one) signs to him
    signatures = []
    if user_id:
        accessible_projects = [project for project in Project.objects.all() if check_view_permissions(user_id, project, strict=True)]
        signatures = Signature.objects.filter(factor__assay__project__in=accessible_projects)

    selected_signature = Signature.objects.get(id=signature_id)
    temp_dir_path = _prepare_temp_folder(task_id, selected_signature, signatures)

    if not temp_dir_path:
        logger.exception("Temp directory with this task id ({}) already exists. Stopping..".format(task_id))
        raise TaskFailure('test')


    run = subprocess.run(['/bin/bash', '/app/tools/run_dist/run_dist.sh', temp_dir_path, job_dir_path, temp_dir_path + selected_signature.tsx_id + ".sign"], capture_output=True)
    logger.info(run.stdout.decode())
    print(run.stdout.decode())
    print(run.stderr.decode())

def _prepare_temp_folder(request_id, signature, additional_signatures):

    temp_dir_path =  "/app/tools/job_dir/temp/" + request_id + "/"

    # Task id SHOUlD be unique, and we SHOUld cleanup afterward..
    if os.path.exists(temp_dir_path):
        return None

    os.mkdir(temp_dir_path)

    shutil.copy2(signature.expression_values_file.path, temp_dir_path)
    for sig in additional_signatures:
        shutil.copy2(sig.expression_values_file.path, temp_dir_path)

    shutil.copy2('/app/tools/admin_data/public.RData', temp_dir_path)

    return temp_dir_path





