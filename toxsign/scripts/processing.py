import os
import shutil
import time
import tempfile
from urllib.request import urlopen
import gzip
import subprocess
import datetime
import time

from toxsign.taskapp.celery import app

from toxsign.projects.views import check_view_permissions
from toxsign.projects.models import Project
from toxsign.signatures.models import Signature
from toxsign.tools.models import PredictionModel
from toxsign.jobs.models import Job

from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

class TaskFailure(Exception):
   pass


def zip_results(path_to_folder, archive_name="archive"):
    if os.path.exists(path_to_folder + '/{}.zip'.format(archive_name)):
        os.remove(path_to_folder + '/{}.zip'.format(archive_name))

    with tempfile.TemporaryDirectory() as dirpath:
        archive_temp_path = shutil.make_archive(dirpath + '/' + archive_name, 'zip', path_to_folder)
        archive_path = shutil.move(archive_temp_path, path_to_folder)

    return archive_path

@app.task(bind=True)
def run_distance(self, signature_id, user_id=None):
    from toxsign.users.models import User
    dt = datetime.datetime.utcnow()
    ztime = time.mktime(dt.timetuple())
    task_id = self.request.id + "_" + str(ztime)

    # Does it work with no rData file? Using only provided signatures?
    if not os.path.exists("/app/toxsign/media/jobs/admin/public.RData"):
        logger.exception("No public.RData file. Stopping..")
        raise TaskFailure('No public.RData file')

    job_dir_path = "/app/toxsign/media/jobs/results/" + task_id + "/"

    if os.path.exists(job_dir_path):
        logger.exception("Result directory {} already exists. Stopping.".format(task_id))
        raise TaskFailure('Result directory already exists')

    os.mkdir(job_dir_path)


    # If is logged, get all available (private one) signs to him
    signatures = []
    if user_id:
        user = User.objects.get(id=user_id)
        accessible_projects = [project for project in Project.objects.exclude(status="PUBLIC") if check_view_permissions(user, project, strict=True, allow_superuser=False)]
        signatures = Signature.objects.filter(factor__assay__project__in=accessible_projects)

    selected_signature = Signature.objects.get(id=signature_id)

    if not selected_signature.expression_values_file:
        logger.exception("Signature {} has no file associated.".format(selected_signature.tsx_id))
        raise TaskFailure("Signature {} has no file associated.".format(selected_signature.tsx_id))

    temp_dir_path = _prepare_temp_folder(task_id, selected_signature, additional_signatures=signatures, add_RData=True)

    if not temp_dir_path:
        logger.exception("Temp directory with this task id ({}) already exists. Stopping..".format(task_id))
        raise TaskFailure('test')

    current_job = Job.objects.get(celery_task_id=self.request.id)
    current_job.results = {'tmp_folder': temp_dir_path}
    current_job.save()

    run = subprocess.run(['/bin/bash', '/app/tools/run_dist/run_dist.sh', temp_dir_path, job_dir_path, temp_dir_path + selected_signature.tsx_id + ".sign"], capture_output=True)

    if not run.returncode == 0:
        if os.path.exists(temp_dir_path):
            shutil.rmtree(temp_dir_path)
        current_job.results['error'] = run.stdout.decode()
        current_job.save()
        logger.exception(run.stderr.decode())
        raise TaskFailure('Error running bash script')

    zip_path = zip_results(job_dir_path)
    # Update job with results
    results = {
        'files': [
            job_dir_path + 'signature.dist'
        ],
        'job_folder': job_dir_path,
        'archive': zip_path,
        'args': {
            'signature_id': signature_id
        }
    }

    current_job.results = results
    current_job.save()

@app.task(bind=True)
def run_enrich(self, signature_id):
    dt = datetime.datetime.utcnow()
    ztime = time.mktime(dt.timetuple())
    task_id = self.request.id + "_" + str(ztime)

    # Does it work with no rData file? Using only provided signatures?
    if not os.path.exists("/app/toxsign/media/jobs/admin/annotation"):
        logger.exception("No annotation file. Stopping..")
        raise TaskFailure('No annotation file')

    job_dir_path = "/app/toxsign/media/jobs/results/" + task_id + "/"

    if os.path.exists(job_dir_path):
        logger.exception("Result directory {} already exists. Stopping.".format(task_id))
        raise TaskFailure('Result directory already exists')

    os.mkdir(job_dir_path)
    selected_signature = Signature.objects.get(id=signature_id)

    if not selected_signature.expression_values_file:
        logger.exception("Signature {} has no file associated.".format(selected_signature.tsx_id))
        raise TaskFailure("Signature {} has no file associated.".format(selected_signature.tsx_id))

    temp_dir_path = _prepare_temp_folder(task_id, selected_signature, additional_signatures=[], add_Homolog=True)

    if not temp_dir_path:
        logger.exception("Temp directory with this task id ({}) already exists. Stopping..".format(task_id))
        raise TaskFailure('test')

    current_job = Job.objects.get(celery_task_id=self.request.id)
    current_job.results = {'tmp_folder': temp_dir_path}
    current_job.save()

    run = subprocess.run(['/bin/bash', '/app/tools/run_enrich/run_enrich.sh', temp_dir_path, job_dir_path, temp_dir_path + selected_signature.tsx_id + ".sign"], capture_output=True)
    logger.info(run.stdout.decode())

    if not run.returncode == 0:
        if os.path.exists(temp_dir_path):
            shutil.rmtree(temp_dir_path)
        current_job.results['error'] = run.stdout.decode()
        current_job.save()
        logger.exception(run.stderr.decode())
        raise TaskFailure('Error running bash script')

    # Update job with results
    zip_path = zip_results(job_dir_path)

    results = {
        'files': [
            job_dir_path + 'signature.enr'
        ],
        'job_folder': job_dir_path,
        'archive': zip_path,
        'args': {
            'signature_id': signature_id
        }
    }


    current_job.results = results
    current_job.save()

@app.task(bind=True)
def run_cluster_dist(self, signature_id, clustering_type):
    dt = datetime.datetime.utcnow()
    ztime = time.mktime(dt.timetuple())
    task_id = self.request.id + "_" + str(ztime)

    if not os.path.exists("/app/toxsign/media/jobs/admin/" + clustering_type + "_method.RData"):
        logger.exception("No method.rDATA file. Stopping")
        raise TaskFailure('No method.rDATA file.')

    job_dir_path = "/app/toxsign/media/jobs/results/" + task_id + "/"

    if os.path.exists(job_dir_path):
        logger.exception("Result directory {} already exists. Stopping.".format(task_id))
        raise TaskFailure('Result directory already exists')

    os.mkdir(job_dir_path)
    selected_signature = Signature.objects.get(id=signature_id)

    if not selected_signature.expression_values_file:
        logger.exception("Signature {} has no file associated.".format(selected_signature.tsx_id))
        raise TaskFailure("Signature {} has no file associated.".format(selected_signature.tsx_id))

    temp_dir_path = _prepare_temp_folder(task_id, selected_signature, additional_signatures=[], add_Cluster_Method=clustering_type)

    if not temp_dir_path:
        logger.exception("Temp directory with this task id ({}) already exists. Stopping..".format(task_id))
        raise TaskFailure('test')

    current_job = Job.objects.get(celery_task_id=self.request.id)
    current_job.results = {'tmp_folder': temp_dir_path}
    current_job.save()

    run = subprocess.run(['/bin/bash', '/app/tools/run_cluster_dist/run_cluster_dist.sh', temp_dir_path, selected_signature.tsx_id + ".sign", job_dir_path], capture_output=True)
    logger.info(run.stdout.decode())

    if not run.returncode == 0:
        if os.path.exists(temp_dir_path):
            pass
            #shutil.rmtree(temp_dir_path)
        current_job.results['error'] = run.stdout.decode()
        current_job.save()
        logger.exception(run.stderr.decode())
        raise TaskFailure('Error running bash script')

    zip_path = zip_results(job_dir_path)

    results = {
        'files': [
            job_dir_path + 'output.txt'
        ],
        'job_folder': job_dir_path,
        'archive': zip_path,
        'args': {
            'signature_id': signature_id,
            'clustering_type': clustering_type
        }
    }

    current_job.results = results
    current_job.save()

@app.task(bind=True)
def run_predict(self, signature_id, model_id):
    dt = datetime.datetime.utcnow()
    ztime = time.mktime(dt.timetuple())
    task_id = self.request.id + "_" + str(ztime)

    # Does it work with no rData file? Using only provided signatures?
    if not os.path.exists("/app/toxsign/media/jobs/admin/mat_chempsy_final_10793.tsv"):
        logger.exception("No chempsy matrix file found. Stopping..")
        raise TaskFailure('No chempsy matrix file found')

    job_dir_path = "/app/toxsign/media/jobs/results/" + task_id + "/"

    if os.path.exists(job_dir_path):
        logger.exception("Result directory {} already exists. Stopping.".format(task_id))
        raise TaskFailure('Result directory already exists')

    os.mkdir(job_dir_path)
    selected_signature = Signature.objects.get(id=signature_id)

    if not selected_signature.expression_values_file:
        logger.exception("Signature {} has no file associated.".format(selected_signature.tsx_id))
        raise TaskFailure("Signature {} has no file associated.".format(selected_signature.tsx_id))

    selected_model = PredictionModel.objects.get(id=model_id)

    if not selected_model.model_file or not selected_model.association_matrix:
        logger.exception("Model {} is missing a file.".format(selected_model.name))
        raise TaskFailure("Model {} is missing a file".format(selected_model.name))

    temp_dir_path = _prepare_temp_folder(task_id, selected_signature, additional_signatures=[], add_Homolog=True, predict_model=selected_model)

    if not temp_dir_path:
        logger.exception("Temp directory with this task id ({}) already exists. Stopping..".format(task_id))
        raise TaskFailure('test')

    current_job = Job.objects.get(celery_task_id=self.request.id)
    current_job.results = {'tmp_folder': temp_dir_path}
    current_job.save()

    run = subprocess.run(['/bin/bash', '/app/tools/run_predict/run_predict.sh', temp_dir_path, selected_signature.name, selected_signature.tsx_id, job_dir_path], capture_output=True)
    logger.info(run.stdout.decode())

    if not run.returncode == 0:
        if os.path.exists(temp_dir_path):
            #shutil.rmtree(temp_dir_path)
            pass
        current_job.results['error'] = run.stdout.decode()
        current_job.save()
        logger.exception(run.stderr.decode())
        raise TaskFailure('Error running bash script')

    # Update job with results
    zip_path = zip_results(job_dir_path)

    results = {
        'files': [
            job_dir_path + 'prediction_results.tsv'
        ],
        'job_folder': job_dir_path,
        'archive': zip_path,
        'args': {
            'signature_id': signature_id,
            'model_id': model_id
        }
    }

    current_job.results = results
    current_job.save()

def _prepare_temp_folder(request_id, signature, additional_signatures=[], add_RData=False, add_Homolog=False, predict_model=None, add_Cluster_Method=False):

    temp_dir_path =  "/app/toxsign/media/jobs/temp/" + request_id + "/"

    # Task id SHOUlD be unique, and we SHOUld cleanup afterward..
    if os.path.exists(temp_dir_path):
        return None

    os.mkdir(temp_dir_path)

    shutil.copy2(signature.expression_values_file.path, temp_dir_path)
    for sig in additional_signatures:
        if sig.expression_values_file and os.path.exists(sig.expression_values_file.path):
            shutil.copy2(sig.expression_values_file.path, temp_dir_path)

    if add_RData:
        shutil.copy2('/app/toxsign/media/jobs/admin/public.RData', temp_dir_path)
    if add_Homolog:
        shutil.copy2('/app/toxsign/media/jobs/admin/annotation', temp_dir_path)

    if predict_model:
        shutil.copy2('/app/toxsign/media/jobs/admin/mat_chempsy_final_10793.tsv', temp_dir_path)
        shutil.copy2(predict_model.model_file.path, temp_dir_path)
        shutil.copy2(predict_model.association_matrix.path, temp_dir_path)

    if add_Cluster_Method:
        shutil.copy2('/app/toxsign/media/jobs/admin/' + add_Cluster_Method + '_method.RData', temp_dir_path+ "method.RData")

    return temp_dir_path
