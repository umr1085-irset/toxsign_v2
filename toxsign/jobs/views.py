import os
from datetime import datetime

from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.views import View
from django.shortcuts import redirect
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import HttpResponse
from mimetypes import guess_type
from django.urls import reverse_lazy

from config.views import paginate

from toxsign.jobs.models import Job
from celery.result import AsyncResult

from django.utils.timezone import now
from datetime import timedelta
from celery.schedules import crontab
from toxsign.taskapp.celery import app


def DetailView(request, pk):
    job = get_object_or_404(Job, pk=pk)
    if job.created_by and not job.created_by == request.user:
        return redirect('/unauthorized')
    file_list = []

    for file in os.listdir(job.output):
        table_content=''
        info = os.path.splitext(file)
        if info[1] == ".matrix" or info[1] == ".tsv" or info[1] == ".info" or info[1] == ".list" :
            df = pd.read_csv(os.path.join(job.output, file), sep="\t")
            df_head = df.head()
            table_content = df_head.to_html(classes=["table", "table-bordered", "table-striped", "table-hover"])
        if info[1] == ".csv":
            df = pd.read_csv(os.path.join(job.output, file), sep=",")
            df_head = df.head()
            table_content = df_head.to_html(classes=["table", "table-bordered", "table-striped", "table-hover"])
        file_list.append({'name':info[0],'ext':info[1], 'table':table_content, 'file':file, 'path':os.path.join(job.output, file)})
    context = {'job':job, 'file_list':file_list}
    return render(request, 'jobs/results.html', context)


def DownloadView(request, pk, file_name):
    job = get_object_or_404(Job, pk=pk)
    file_path = os.path.join(job.output, file_name)

    with open(file_path, 'rb') as f:
        response = HttpResponse(f, content_type=guess_type(file_path)[0])
        response['Content-Length'] = len(response.content)
        return response


class RunningJobsView(generic.ListView):
    model = Job
    template_name = 'jobs/running_jobs.html'

    def get_context_data(self, **kwargs):
        context = super(RunningJobsView, self).get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            jobs = Job.objects.filter(created_by__exact=self.request.user.id)
        else:
            jobs = Job.objects.filter(created_by=None)
        jobs = jobs.order_by('-id')
        jobs = paginate(jobs, self.request.GET.get('jobs'), 10)
        for job in jobs:
            if job.status == "PENDING":
                job.status = AsyncResult(job.celery_task_id).state
                if job.status != "PENDING":
                    job.save()
        context['jobs_list'] = jobs
        return context

def Delete_job(request, pk):
    job = get_object_or_404(Job, pk=pk)
    # Only allow job owner to delete. Anonymous job should not be deleted. Cron will do it
    if not job.created_by or not job.created_by == request.user:
        return redirect('/unauthorized')

    job.delete()
    context = {}
    context['jobs_list'] = Job.objects.filter(created_by__exact=request.user.id)
    for job in context['jobs_list']:
        if job.status != "PENDING":
            job.status = AsyncResult(job.celery_task_id).state
            job.save()

    return render(request, 'jobs/running_jobs.html', context)

@app.on_after_configure.connect
def cron_cleanup(sender, **kwargs):
    sender.add_periodic_task(
        crontab(hour=0, minute=0, day_of_week=1),
        cleanup_jobs.s(),
    )

@app.task
def cleanup_jobs():
    # Clean anonymous jobs older than 7 days
    Job.objects.filter(updated_at__lte= now()-timedelta(days=7), created_by=None).delete()
    # Clean pending jobs?

