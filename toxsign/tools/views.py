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
from toxsign.tools.models import Tool, Category
import toxsign.tools.forms as forms
from toxsign.jobs.models import Job
from toxsign.signatures.models import Signature

from django.conf import settings
from toxsign.taskapp.celery import app



from time import sleep
# Create your views here.
class IndexView(LoginRequiredMixin, generic.ListView):
    template_name = 'tools/index.html'
    context_object_name = 'category_list'

    def get_queryset(self):
        return Category.objects.exclude(category_of=None)

def DetailView(request, toolid):
    model = Tool
    template_name = 'tools/detail.html'
    # Or 404
    tool = Tool.objects.get(id=toolid)
    # Get form attached to the tool
    # Need an error management here
    form_function = getattr(forms, tool.form_name)
    data = dict()
    if request.method == 'POST':
            #data = request.POST
            # Do something here with the args
            data = {}
            # Hacky hacky: We need to pass the values, but request.POST will only contain string when passed to a function. Meaning lists will be converted to the last element
            # So we call getlist on all arguments, to convert them as list
            for key in request.POST:
                if not key == "csrfmiddlewaretoken" and not key == "save":
                    data[key] = request.POST.getlist(key)
            task = print_command_line.delay(tool.id, data)
            create_job("test", "/bla", request.user, task.id)
            return(redirect(reverse("jobs:running_jobs")))
    else:
        projects = get_objects_for_user(request.user, 'view_project', Project)
        arguments = tool.arguments
        form = form_function(projects=projects, arguments=arguments)
        context = {'tool': tool, 'form':form}
        return render(request, 'tools/detail.html', context)

def create_job(title, output, owner, task_id):
    # Add checks?
    job = Job(
            title = title,
            output = output,
            created_by = owner,
            celery_task_id = task_id
        )
    job.save()


# Move this to task.py
@app.task
def print_command_line(tool_id, args):
    tool = Tool.objects.get(id=tool_id)
    string = "{} ".format(tool.script_file)
    for argument in tool.arguments.all():
        if argument.label in args:
            if argument.argument_type.type == "Signature":
                string += args_to_string(argument.parameter, args[argument.label], Signature, "expression_values_file", True)
            else:
                string += args_to_string(argument.parameter, args[argument.label])
    print(string)

def args_to_string(parameter, value_list, model=None, field=None, is_file=False):
    string = ""
    # If model, get the entities
    if model:
        # We can access foreign key fields with the field__value syntax, but not for fileField..
        # SO we have to query the whole thing, and call getattr twice
        if is_file:
            values = model.objects.filter(id__in=value_list)
            for value in values:
                string += "{} {} ".format(parameter, getattr(getattr(value,field), "path"))
        else:
            values = model.objects.filter(id__in=value_list).values(field)
            for value in values:
                string += "{} {} ".format(parameter, value[field])
    else:
        for value in value_list:
            string += "{} {}".format(parameter, value)

    return string




