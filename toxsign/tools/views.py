import os, sys, json
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

    return render(request, 'tools/distance_analysis_results.html', {'job': job})

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

        df = pd.read_csv(file_path, sep="\t", encoding="latin1")

        df = df.drop(columns=['HomologeneIds'])
        filters = json.loads(request.POST['terms'])
        for filter in filters:
            try:
                value = float(filter['filter_number'])
            except:
                continue

            column_name = filter['filter_type']
            # Don't trust user input
            if column_name not in df.columns:
                continue

            if filter['filter_adjust'] == 'lt':
                df = df[df[column_name].lt(value)]
            elif filter['filter_adjust'] == 'gt':
                df = df[df[column_name].gt(value)]

        column_dict = {}
        current_order = ""
        current_order_type = ""
        for column in df.columns:
            column_dict[column]={"filter": ""}
        request_ordered_column = request.POST.get('ordered_column')
        if request_ordered_column:
            request_order = request.POST.get('order', "")
            if request_order == "asc":
                df  = df.sort_values(by=[request_ordered_column])
                column_dict[request_ordered_column]['filter'] = 'asc'
                current_order = request_ordered_column
                current_order_type = "asc"
            elif request_order == "desc":
                df  = df.sort_values(by=[request_ordered_column], ascending=False)
                column_dict[request_ordered_column]['filter'] = 'desc'
                current_order = request_ordered_column
                current_order_type= "desc"

        page = request.POST.get('request_page')
        sigs =_paginate_table(df, page)
        context = {'sigs': sigs, 'columns': column_dict, 'current_order':current_order, 'current_order_type':current_order_type, 'job': job}
        data = {
            'table' : render_to_string('tools/partial_distance_results_table.html', context, request=request),
            'current_order': current_order,
            'current_order_type': current_order_type,
            'current_page': sigs.number
        }
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
    job = get_object_or_404(Job, id=job_id)
    if not job.created_by == request.user:
        return redirect('/unauthorized')

    return render(request, 'tools/functional_analysis_results.html', {'job': job})

def functional_analysis_full_table(request, job_id):
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

        df = pd.read_csv(file_path, sep="\t", encoding="latin1")
        df = df.drop(columns=['HomologeneIds'])

        filters = json.loads(request.POST['terms'])
        for filter in filters:
            try:
                value = float(filter['filter_number'])
            except:
                continue
            column_name = filter['filter_type']
            # Don't trust user input
            if column_name not in df.columns:
                continue

            if filter['filter_adjust'] == 'lt':
                df = df[df[column_name].lt(value)]
            elif filter['filter_adjust'] == 'gt':
                df = df[df[column_name].gt(value)]

        column_dict = {}
        for column in df.columns:
            if not column == "Type":
                column_dict[column]={"filter": ""}

        process_table = _paginate_table(df[df.Type == "Process"].drop(columns=['Type']), None)
        component_table = _paginate_table(df[df.Type == "Component"].drop(columns=['Type']), None)
        phenotype_table= _paginate_table(df[df.Type == "Phenotype"].drop(columns=['Type']), None)
        function_table= _paginate_table(df[df.Type == "Function"].drop(columns=['Type']), None)

        data = {
            'Process': process_table,
            'Component': component_table,
            'Function': function_table,
            'Phenotype': phenotype_table,
        }
        context = {
            'data': data,
            'columns': column_dict,
            'job': job
        }
        data = {
            'table' : render_to_string('tools/partial_enrich_full_table.html', context, request=request),
            'types': ['Process','Component','Function', 'Phenotype']
        }
        return JsonResponse(data)

def functional_analysis_partial_table(request, job_id, type):
        # Due to potential complexity in arguments (multiples filters), we pass it as a POST instead of GET
        if not request.method == 'POST':
            return JsonResponse({})

        if type not in ["Process", "Component", "Phenotype", "Function"]:
            return JsonResponse({})

        job = get_object_or_404(Job, id=job_id)
        if not job.created_by == request.user:
            return JsonResponse({})

        file_path = job.results['files'][0]
        selected_signature_id = job.results['args']['signature_id']

        if not os.path.exists(file_path):
            # What do do?
            pass

        df = pd.read_csv(file_path, sep="\t", encoding="latin1")
        df = df.drop(columns=['HomologeneIds'])

        filters = json.loads(request.POST['terms'])
        for filter in filters:
            try:
                value = float(filter['filter_number'])
            except:
                continue
            column_name = filter['filter_type']
            # Don't trust user input
            if column_name not in df.columns:
                continue

            if filter['filter_adjust'] == 'lt':
                df = df[df[column_name].lt(value)]
            elif filter['filter_adjust'] == 'gt':
                df = df[df[column_name].gt(value)]

        column_dict = {}
        current_order = ""
        current_order_type = ""

        for column in df.columns:
            if not column == "Type":
                column_dict[column]={"filter": ""}

        request_ordered_column = request.POST.get('ordered_column')
        if request_ordered_column:
            request_order = request.POST.get('order', "")
            if request_order == "asc":
                df  = df.sort_values(by=[request_ordered_column])
                column_dict[request_ordered_column]['filter'] = 'asc'
                current_order = request_ordered_column
                current_order_type = "asc"
            elif request_order == "desc":
                df  = df.sort_values(by=[request_ordered_column], ascending=False)
                column_dict[request_ordered_column]['filter'] = 'desc'
                current_order = request_ordered_column
                current_order_type= "desc"

        page = request.POST.get('request_page')
        table = _paginate_table(df[df.Type == type].drop(columns=['Type']), page)

        context = {
            'table': table,
            'columns': column_dict,
            'type': type,
            'job': job
        }
        data = {
            'table' : render_to_string('tools/partial_enrich_single_table.html', context, request=request),
            'type': type,
            'current_order': current_order,
            'current_order_type': current_order_type,
            'current_page': table.number
        }
        return JsonResponse(data)

def prediction_tool(request):
    pass


def _create_job(title, owner, task_id, tool):
    # Add checks?
    job = Job(
            title = title,
            created_by = owner,
            celery_task_id = task_id,
            running_tool = tool
        )
    job.save()

def _paginate_table(dataframe, page):
    paginator = Paginator(dataframe.apply(lambda df: df.values,axis=1),10)
    try:
        result = paginator.page(page)
    except PageNotAnInteger:
        result = paginator.page(1)
    except EmptyPage:
        result = paginator.page(paginator.num_pages)
    return result


