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
from django.http import JsonResponse
from django.contrib import messages

import uuid
import shutil

from celery.result import AsyncResult

from guardian.shortcuts import get_objects_for_user
from toxsign.projects.models import Project
from toxsign.projects.views import check_view_permissions
from toxsign.tools.models import Tool
from toxsign.tools.forms import *
from toxsign.jobs.models import Job

from django.conf import settings
from toxsign.taskapp.celery import app

from time import sleep
# Create your views here.
class IndexView(LoginRequiredMixin, generic.ListView):
    template_name = 'tools/index.html'
    context_object_name = 'tools_list'

    def get_queryset(self):
        """
        Return the last five published questions (not including those set to be
        published in the future).
        """
        return Tool.objects.filter(
            created_at__lte=timezone.now()
        ).order_by('-created_at')[:5]

def DetailView(request, toolid):
    model = Tool
    template_name = 'tools/detail.html'
    tool = Tool.objects.get(id=toolid)

    data = dict()
    if request.method == 'POST':
            data = request.post
            # Do something here
#        task = show_hello_world.delay()
#        create_job("test", "/bla", request.user, task.id)
    else:
        projects = get_objects_for_user(request.user, 'view_project', Project)
        arguments_order = tool.arguments_order
        form = test_form(projects=projects, arguments_order=arguments_order)
        context = {'tool': tool, 'form':form}
        return render(request, 'tools/detail.html', context)


def create_job(title, output, owner, task_id):
    # Add checks?
    job = Job(
            title="Test",
            output="/bla",
            created_by=request.user,
            celery_task_id = task.id
        )
    job.save()


# Move this to task.py
@app.task
def show_hello_world():
    sleep(3600)
    print("-"*25)
    print("Printing Hello from Celery")
    print("-"*25)
