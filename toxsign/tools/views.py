import os, sys
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
import pandas as pd

from celery.result import AsyncResult
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template.loader import render_to_string

from guardian.shortcuts import get_objects_for_user
from toxsign.projects.models import Project
from toxsign.projects.views import check_view_permissions
from toxsign.tools.models import Tool, Category
import toxsign.tools.forms as forms
from toxsign.jobs.models import Job
from toxsign.signatures.models import Signature
from toxsign.projects.models import Project

from django.conf import settings
from toxsign.taskapp.celery import app

from toxsign.scripts.processing import run_distance, run_enrich


from time import sleep
# Create your views here.
class IndexView(generic.ListView):
    template_name = 'tools/index.html'
    context_object_name = 'category_list'

    def get_queryset(self):
        return Category.objects.exclude(category_of=None)

def distance_analysis_tool(request):

    accessible_projects = [project for project in Project.objects.all() if check_view_permissions(request.user, project)]
    signatures = Signature.objects.filter(factor__assay__project__in=accessible_projects)

    if request.method == 'POST':
        form = forms.signature_compute_form(request.POST, signatures=signatures)
        if form.is_valid():
            signature_id = request.POST['signature']
            # Make sure it's selected from available sigs
            if not signatures.filter(id=signature_id).exists:
                return redirect('/unauthorized')
            job_name = request.POST['job_name']
            tool = Tool.objects.get(name="Signature enrichment analysis")
            if request.user.is_authenticated:
                task = run_distance.delay(signature_id, request.user.id)
            else:
                task = run_distance.delay(signature_id)

            _create_job(job_name, request.user, task.id, tool)
            return(redirect(reverse("jobs:running_jobs")))

        else:
            context = {'form':form}
            return render(request, 'tools/run_dist.html', context)

        sig_id = request.POST['signature']
        job_name = request.POST['job_name']

    else:
        form = forms.signature_compute_form(signatures=signatures)
        context = {'form':form}
        return render(request, 'tools/run_dist.html', context)

def distance_analysis_results(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    if not job.created_by == request.user:
        return redirect('/unauthorized')

    return render(request, 'tools/visualize.html', {})

def distance_analysis_table(request, job_id):
        # Due to potential complexity in arguments (multiples filters), we pass it as a POST instead of GET
        if not request.method == 'POST':
            return JsonResponse({})
        job = get_object_or_404(Job, id=job_id)
        if not job.created_by == request.user:
            return JsonResponse({})

        file_path = job.results['files'][0]
        selected_signature_id = job.results['args']['signature_id']

        if not os.path.exists(file_path):
            # What do do?
            pass
        # Should do this in separate function to allow ajax calls
        df = pd.read_csv(file_path, sep="\t", encoding="latin1")
        #df[df.Ratio.gt(0.5)]
        df = df.drop(columns=['HomologeneIds'])
        column_dict = {}
        current_order = ""
        current_order_type = ""
        for column in df.columns:
            column_dict[column]={"filter": "}
        # table_content = df.to_html(classes=["table","table-bordered","table-striped"], justify='center')
        request_ordered_column = request.POST.get('ordered_column')
        if request_ordered_column:
            request_order = request.POST.get('order', "")
            if request_ordered_column == "asc":
                df  = df.sort_values(by=[asc])
                column_dict[asc]['filter'] = 'asc'
                current_order = asc
                current_order_type= "asc"
            elif request_ordered_column == "desc":
                df  = df.sort_values(by=[desc], ascending=False)
                column_dict[asc]['filter'] = 'desc'
                current_order = desc
                current_order_type= "desc"

        paginator = Paginator(df.apply(lambda df: df.values,axis=1),10)
        page = request.POST.get('page')
        try:
            sigs = paginator.page(page)
        except PageNotAnInteger:
            sigs = paginator.page(1)
        except EmptyPage:
            sigs = paginator.page(paginator.num_pages)

        context = {'sigs': sigs, 'columns': column_dict, 'current_order':current_order, 'current_order_type':current_order_type, 'job': job}
        data['table'] = render_to_string(request, 'tools/partial_results_table.html', context, request=request)
        return JsonResponse(data)

def functional_analysis_tool(request):

    accessible_projects = [project for project in Project.objects.all() if check_view_permissions(request.user, project)]
    signatures = Signature.objects.filter(factor__assay__project__in=accessible_projects)

    if request.method == 'POST':
        form = forms.signature_compute_form(request.POST, signatures=signatures)
        if form.is_valid():
            signature_id = request.POST['signature']
            # Make sure it's selected from available sigs
            if not signatures.filter(id=signature_id).exists:
                return redirect('/unauthorized')
            tool = Tool.objects.get(name="Functional enrichment analysis")
            job_name = request.POST['job_name']
            task = run_enrich.delay(signature_id)
            _create_job(job_name, request.user, task.id, tool)
            return(redirect(reverse("jobs:running_jobs")))

        else:
            context = {'form':form}
            return render(request, 'tools/run_dist.html', context)

        sig_id = request.POST['signature']
        job_name = request.POST['job_name']

    else:
        form = forms.signature_compute_form(signatures=signatures)
        context = {'form':form}
        return render(request, 'tools/run_dist.html', context)

def functional_analysis_results(request, job_id):
    pass

def prediction_tool(request):
    pass

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
            _create_job("test", request.user, task.id, tool.id)
            return(redirect(reverse("jobs:running_jobs")))
    else:
        projects = get_objects_for_user(request.user, 'view_project', Project)
        arguments = tool.arguments
        form = form_function(projects=projects, arguments=arguments)
        context = {'tool': tool, 'form':form}
        return render(request, 'tools/detail.html', context)

def _create_job(title, owner, task_id, tool):
    # Add checks?
    job = Job(
            title = title,
            created_by = owner,
            celery_task_id = task_id,
            running_tool = tool
        )
    job.save()

# Move this to task.py
# This will ignore parameters not registered in the tool....
@app.task(bind=True)
def print_command_line(self, tool_id, args):
    tool = Tool.objects.get(id=tool_id)
    string = "{} ".format(tool.script_file)
    for argument in tool.arguments.all():
        if argument.argument_type.type == "Job_id":
            string += "{} {}".format(argument.label, self.request.id)
            continue
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
