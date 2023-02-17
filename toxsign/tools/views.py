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
import json

from celery.result import AsyncResult
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template.loader import render_to_string

from guardian.shortcuts import get_objects_for_user
from toxsign.projects.models import Project
from toxsign.projects.views import check_view_permissions
from toxsign.tools.models import Tool, Category, PredictionModel
import toxsign.tools.forms as forms
from toxsign.jobs.models import Job
from toxsign.signatures.models import Signature
from toxsign.projects.models import Project

from toxsign.clusters.models import Cluster

from django.conf import settings
from toxsign.taskapp.celery import app

from toxsign.scripts.processing import run_distance, run_enrich, run_predict, run_cluster_dist
from toxsign.users.views import is_viewable


from time import sleep
# Create your views here.
class IndexView(generic.ListView):
    template_name = 'tools/index.html'
    context_object_name = 'category_list'

    def get_queryset(self):
        return Category.objects.exclude(category_of=None)

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['selected_sig'] = self.request.GET.get('selected')
        return context


def distance_analysis_tool(request):

    excluded_projects = Project.objects.exclude(status="PUBLIC")
    excluded_projects_id_list = [project.id for project in excluded_projects if not check_view_permissions(request.user, project)]
    signatures = Signature.objects.exclude(up_gene_number=0, down_gene_number=0).exclude(factor__assay__project__id__in=excluded_projects_id_list)

    selected_signature = None
    if request.GET.get('selected'):
        selected_signature = signatures.filter(tsx_id=request.GET.get('selected'))
        if selected_signature:
            selected_signature = selected_signature[0]

    if request.method == 'POST':
        form = forms.signature_compute_form(request.POST, signatures=signatures, selected_signature=selected_signature)
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
        form = forms.signature_compute_form(signatures=signatures, selected_signature=selected_signature)
        context = {'form':form}
        return render(request, 'tools/run_dist.html', context)

def distance_analysis_results(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    if not is_viewable(job, request.user):
        return redirect('/unauthorized')

    sig_id = job.results['args']['signature_id']

    sig = Signature.objects.get(id=sig_id)
    return render(request, 'tools/distance_analysis_results.html', {'job': job, 'sig': sig})

def distance_analysis_table(request, job_id):
        # Due to potential complexity in arguments (multiples filters), we pass it as a POST instead of GET
        if not request.method == 'POST':
            return JsonResponse({})
        job = get_object_or_404(Job, id=job_id)

        if not is_viewable(job, request.user):
            return JsonResponse({})

        file_path = job.results['files'][0]
        selected_signature_id = job.results['args']['signature_id']

        if not os.path.exists(file_path):
            # What do do?
            pass

        df = pd.read_csv(file_path, sep="\t", encoding="latin1")

        df = df.drop(columns=['HomologeneIds', "Zscore"])
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
            elif filter['filter_adjust'] == 'le':
                df = df[df[column_name].le(value)]
            elif filter['filter_adjust'] == 'ge':
                df = df[df[column_name].ge(value)]

        column_dict = {}
        current_order = ""
        current_order_type = ""
        for column in df.columns:
            column_dict[column]={"filter": ""}
        request_ordered_column = request.POST.get('ordered_column')
        if not request_ordered_column:
            df  = df.sort_values(by=['Correlation dist'], ascending=False)
            column_dict["Correlation dist"]['filter'] = 'desc'
            current_order = "Correlation dist"
            current_order_type= "desc"
        else:
            request_order = request.POST.get('order', "")
            if request_order == "asc":
                if request_ordered_column == "Signature":
                    df['sort'] = df['Signature'].str.extract(r'TSS(\d+)', expand=False).astype(int)
                    df  = df.sort_values(by=['sort'])
                    df = df.drop('sort', axis=1)
                else:
                    df  = df.sort_values(by=[request_ordered_column])
                column_dict[request_ordered_column]['filter'] = 'asc'
                current_order = request_ordered_column
                current_order_type = "asc"
            elif request_order == "desc":
                if request_ordered_column == "Signature":
                    df['sort'] = df['Signature'].str.extract(r'TSS(\d+)', expand=False).astype(int)
                    df  = df.sort_values(by=['sort'], ascending=False)
                    df = df.drop('sort', axis=1)
                else:
                    df  = df.sort_values(by=[request_ordered_column], ascending=False)
                column_dict[request_ordered_column]['filter'] = 'desc'
                current_order = request_ordered_column
                current_order_type= "desc"

        page = request.POST.get('request_page')
        sigs =_paginate_table(df, page, 15, is_sig=True)
        context = {'sigs': sigs, 'columns': column_dict, 'current_order':current_order, 'current_order_type':current_order_type, 'job': job}
        data = {
            'table' : render_to_string('tools/partial_distance_results_table.html', context, request=request),
            'current_order': current_order,
            'current_order_type': current_order_type,
            'current_page': sigs.number
        }
        return JsonResponse(data)

def functional_analysis_tool(request):

    excluded_projects = Project.objects.exclude(status="PUBLIC")
    excluded_projects_id_list = [project.id for project in excluded_projects if not check_view_permissions(request.user, project)]
    signatures = Signature.objects.exclude(up_gene_number=0, down_gene_number=0).exclude(factor__assay__project__id__in=excluded_projects_id_list)

    selected_signature = None
    if request.GET.get('selected'):
        selected_signature = signatures.filter(tsx_id=request.GET.get('selected'))
        if selected_signature:
            selected_signature = selected_signature[0]

    if request.method == 'POST':
        form = forms.signature_compute_form(request.POST, signatures=signatures, selected_signature=selected_signature)
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
        form = forms.signature_compute_form(signatures=signatures, selected_signature=selected_signature)
        context = {'form':form}
        return render(request, 'tools/run_enrich.html', context)

def functional_analysis_results(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    if not is_viewable(job, request.user):
        return redirect('/unauthorized')

    sig_id = job.results['args']['signature_id']

    sig = Signature.objects.get(id=sig_id)

    return render(request, 'tools/functional_analysis_results.html', {'job': job, "sig": sig})

def functional_analysis_full_table(request, job_id):
        # Due to potential complexity in arguments (multiples filters), we pass it as a POST instead of GET
        if not request.method == 'POST':
            return JsonResponse({})
        job = get_object_or_404(Job, id=job_id)

        if not is_viewable(job, request.user):
            return JsonResponse({})

        file_path = job.results['files'][0]
        selected_signature_id = job.results['args']['signature_id']

        if not os.path.exists(file_path):
            # What do do?
            pass

        df = pd.read_csv(file_path, sep="\t", encoding="latin1")
        df = df.drop(columns=['HomologeneIds'])

        df.columns = ["Type", "Term", "r", "R", "n", "N", "r/R", "Pvalue", "Adj PValue"]

        ordered_columns = ["Type", "Term", "Adj PValue", "Pvalue", "r/R", "r", "R", "n", "N"]

        df = df[ordered_columns]

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
            elif filter['filter_adjust'] == 'le':
                df = df[df[column_name].le(value)]
            elif filter['filter_adjust'] == 'ge':
                df = df[df[column_name].ge(value)]

        column_dict = {}
        for column in df.columns:
            if not column == "Type":
                column_dict[column]={"filter": ""}

        process_table = _paginate_table(df[df.Type == "Process"].drop(columns=['Type']), None, 15)
        component_table = _paginate_table(df[df.Type == "Component"].drop(columns=['Type']), None, 15)
        phenotype_table= _paginate_table(df[df.Type == "Phenotype"].drop(columns=['Type']), None, 15)
        function_table= _paginate_table(df[df.Type == "Function"].drop(columns=['Type']), None, 15)

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
        if not is_viewable(job, request.user):
            return JsonResponse({})

        file_path = job.results['files'][0]
        selected_signature_id = job.results['args']['signature_id']

        if not os.path.exists(file_path):
            # What do do?
            pass

        df = pd.read_csv(file_path, sep="\t", encoding="latin1")
        df = df.drop(columns=['HomologeneIds'])

        df.columns = ["Type", "Term", "r", "R", "n", "N", "r/R", "Pvalue", "Adj PValue"]
        ordered_columns = ["Type", "Term", "Adj PValue", "Pvalue", "r/R", "r", "R", "n", "N"]

        df = df[ordered_columns]

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
            elif filter['filter_adjust'] == 'le':
                df = df[df[column_name].le(value)]
            elif filter['filter_adjust'] == 'ge':
                df = df[df[column_name].ge(value)]

        column_dict = {}
        current_order = ""
        current_order_type = ""

        search_value = request.POST.get('search_value')
        if search_value:
            df = df[df['Term'].str.contains(search_value)]

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
        table = _paginate_table(df[df.Type == type].drop(columns=['Type']), page, 15)

        context = {
            'table': table,
            'columns': column_dict,
            'search_value': search_value,
            'type': type,
            'job': job
        }
        data = {
            'table' : render_to_string('tools/partial_enrich_single_table.html', context, request=request),
            'columns': render_to_string('tools/partial_enrich_single_columns.html', context, request=request),
            'paginate': render_to_string('tools/partial_enrich_single_paginate.html', context, request=request),
            'type': type,
            'search_value': search_value,
            'current_order': current_order,
            'current_order_type': current_order_type,
            'current_page': table.number
        }
        return JsonResponse(data)

def prediction_tool(request):

    excluded_projects = Project.objects.exclude(status="PUBLIC")
    excluded_projects_id_list = [project.id for project in excluded_projects if not check_view_permissions(request.user, project)]
    signatures = Signature.objects.exclude(up_gene_number=0, down_gene_number=0).exclude(factor__assay__project__id__in=excluded_projects_id_list)

    selected_signature = None
    if request.GET.get('selected'):
        selected_signature = signatures.filter(tsx_id=request.GET.get('selected'))
        if selected_signature:
            selected_signature = selected_signature[0]

    if request.method == 'POST':
        form = forms.prediction_compute_form(request.POST, signatures=signatures, selected_signature=selected_signature)
        if form.is_valid():
            signature_id = request.POST.get('signature')
            # Make sure it's selected from available sigs
            if not signature_id or not signatures.filter(id=signature_id).exists:
                return redirect('/unauthorized')

            model_id = request.POST.get('model')
            if not model_id or not PredictionModel.objects.filter(id=model_id).exists:
                return redirect('/unauthorized')

            tool = Tool.objects.get(name="ChemPSy - Prediction")
            job_name = request.POST.get('job_name', "Prediction job")
            task = run_predict.delay(signature_id, model_id)
            _create_job(job_name, request.user, task.id, tool)
            return(redirect(reverse("jobs:running_jobs")))

        else:
            context = {'form':form}
            return render(request, 'tools/run_predict.html', context)

    else:
        form = forms.prediction_compute_form(signatures=signatures, selected_signature=selected_signature)
        context = {'form':form}
        return render(request, 'tools/run_predict.html', context)

def cluster_dist_tool(request):

    excluded_projects = Project.objects.exclude(status="PUBLIC")
    excluded_projects_id_list = [project.id for project in excluded_projects if not check_view_permissions(request.user, project)]
    signatures = Signature.objects.exclude(up_gene_number=0, down_gene_number=0).exclude(factor__assay__project__id__in=excluded_projects_id_list)
    selected_signature = None
    if request.GET.get('selected'):
        selected_signature = signatures.filter(tsx_id=request.GET.get('selected'))
        if selected_signature:
            selected_signature = selected_signature[0]

    if request.method == 'POST':
        form = forms.signature_cluster_compute_form(request.POST, signatures=signatures, selected_signature=selected_signature)
        if form.is_valid():
            signature_id = request.POST.get('signature')

            # Make sure it's selected from available sigs
            if not signature_id or not signatures.filter(id=signature_id).exists:
                return redirect('/unauthorized')

            cluster_type = request.POST.get('cluster_type')

            if cluster_type not in ['euclidean', 'correlation']:
                return redirect('/unauthorized')

            tool = Tool.objects.get(name="ChemPSy - Spatial prediction")
            job_name = request.POST.get('job_name', "Cluster distance job")
            task = run_cluster_dist.delay(signature_id, cluster_type)
            _create_job(job_name, request.user, task.id, tool)
            return(redirect(reverse("jobs:running_jobs")))

        else:
            context = {'form':form}
            return render(request, 'tools/run_cluster_dist.html', context)

        sig_id = request.POST['signature']
        job_name = request.POST['job_name']

    else:
        form = forms.signature_cluster_compute_form(signatures=signatures, selected_signature=selected_signature)
        context = {'form':form}
        return render(request, 'tools/run_cluster_dist.html', context)

def cluster_dist_results(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    if not is_viewable(job, request.user):
        return redirect('/unauthorized')

    file_path = job.results['files'][0]
    selected_signature_id = job.results['args']['signature_id']
    selected_distance_id = job.results['args']['clustering_type']

    signature = Signature.objects.get(id=selected_signature_id)
    chemical = "No chemical associated"
    if signature.factor.chemical_subfactor_of:
        chemical_list = []
        for chemical in signature.factor.chemical_subfactor_of.all():
            if chemical.chemical:
                chemical_list.append(chemical.chemical.name)
            elif chemical.chemical_slug:
                chemical_list.append(chemical.chemical_slug)
        chemical = "{}".format(", ".join(chemical_list))

    df = pd.read_csv(file_path, sep="\t", encoding="latin1")
    df = df.set_index('Class')
    df = df.drop(['X', 'Y', 'Sample'])
    df = df.drop(columns=['Sign'])

    if selected_distance_id == "euclidean":
        df = df.drop(['Correlation - Medoid', 'Correlation - Centroid', 'Correlation - Closest', 'Correlation - PCA(Medoid)', 'Correlation - PCA(Centroid)', 'Euclidean distance - PCA(Medoid)', 'Euclidean distance - PCA(Centroid)'])
        order_type="asc"

    elif selected_distance_id == "correlation":
        df = df.drop(['Euclidean distance - Medoid', 'Euclidean distance - Centroid', 'Euclidean distance - Closest', 'Euclidean distance - PCA(Medoid)', 'Euclidean distance - PCA(Centroid)', 'Correlation - PCA(Medoid)', 'Correlation - PCA(Centroid)'])
        order_type="desc"

    clusters = []
    for cluster_name in df.columns:
        cluster_id = cluster_name.split(".")[-1]
        cluster = Cluster.objects.filter(distance_method=selected_distance_id, cluster_id=cluster_id)
        if cluster:
            clusters.append({'cluster': cluster[0], 'value': df[cluster_name].values})
    columns = df.index.values

    return render(request, 'tools/run_cluster_dist_results.html', {'columns': columns, 'clusters': clusters, 'distance_type': selected_distance_id, 'signature': signature, 'chemical': chemical, "order_type": order_type})

def prediction_tool_results(request, job_id):

    job = get_object_or_404(Job, id=job_id)

    if not is_viewable(job, request.user):
        return redirect('/unauthorized')

    file_path = job.results['files'][0]
    selected_signature_id = job.results['args']['signature_id']
    selected_model_id = job.results['args']['model_id']

    signature  = get_object_or_404(Signature, id=selected_signature_id)

    chemical = "No chemical associated"
    if signature.factor.chemical_subfactor_of:
        chemical_list = []
        for chemical in signature.factor.chemical_subfactor_of.all():
            if chemical.chemical:
                chemical_list.append(chemical.chemical.name)
            elif chemical.chemical_slug:
                chemical_list.append(chemical.chemical_slug)
        chemical = "{}".format(", ".join(chemical_list))

    model = get_object_or_404(PredictionModel, id=selected_model_id)
    type = model.parameters.get("cluster_distance_type")

    if not type:
        # What to do?
        pass

    if not os.path.exists(file_path):
        # What do do?
        pass

    # Will need to manage multiple signature at some point
    df = pd.read_csv(file_path, sep="\t", encoding="latin1")
#    df = df[df['x'] > 0.05]

    clusters = []
    for cluster_name in df.index.values:
        cluster_id = cluster_name.replace("Group_", "")
        cluster = Cluster.objects.filter(distance_method=type, cluster_id=cluster_id)
        if cluster:
            clusters.append({'cluster': cluster[0], 'value': df["x"][cluster_name]})

    json_data = _format_graph_data(clusters)

    context = {
        "clusters": clusters,
        "json_data": json.dumps(json_data),
        "chemical": chemical,
        "signature": signature,
        "model": model

    }
    return render(request, 'tools/run_predict_results.html', context)

def _format_graph_data(data):

    layout = {
        "title": "Probability that the sample belongs to a cluster",
        "bargap": 0.9,
        "yaxis": {
            "automargin": True,
            "autorange":"reversed"
        },
    };

    return {
        "data": [{
            "x": [cluster['value'] for cluster in data],
            "y": ["<a href='{}'>Cluster {} </a>".format(reverse('clusters:details', kwargs={'type': cluster['cluster'].distance_method, 'clrid':cluster['cluster'].cluster_id}), cluster['cluster'].cluster_id) for cluster in data],
            "type": "bar",
            "orientation": "h",
            "textposition": 'auto',
        }],
        "layout": layout
    }


def _create_job(title, owner, task_id, tool, type="TOOL"):
    # Add checks?
    if not owner.is_authenticated:
        owner=None

    job = Job(
            title = title,
            created_by = owner,
            celery_task_id = task_id,
            running_tool = tool,
            type = type
        )
    job.save()

def _paginate_table(dataframe, page, max_size=10, is_sig=False):
    paginator = Paginator(dataframe.apply(lambda df: df.values,axis=1), max_size)
    try:
        result = paginator.page(page)
    except PageNotAnInteger:
        result = paginator.page(1)
    except EmptyPage:
        result = paginator.page(paginator.num_pages)

    if is_sig:
        for data in result:
            sig_id = data[0]
            sig = Signature.objects.get(tsx_id=sig_id)
            html = "<a href='{}' target='_blank'>{} - {}</a>".format(reverse("signatures:detail", kwargs={"sigid": sig.tsx_id}), sig.tsx_id ,sig.name)
            data[0] = html

    return result
