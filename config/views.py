from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.views import generic
from django.views.generic import DetailView, ListView, RedirectView, UpdateView
from django.http import HttpResponse, JsonResponse
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


import json

from toxsign.assays.models import Assay, Factor
from toxsign.projects.models import Project
from toxsign.signatures.models import Signature
from toxsign.studies.models import Study
from toxsign.projects.views import check_view_permissions



def HomeView(request):
        context = {}
        return render(request, 'pages/home.html',context)

def autocompleteModel(request):
    query = request.GET.get('q')
    results_projects = Project.objects.filter(Q(name__icontains=query) | Q(description__icontains=query) | Q(tsx_id__icontains=query))
    results_studies = Study.objects.filter(Q(name__icontains=query) | Q(description__icontains=query) | Q(tsx_id__icontains=query))
    results_signatures = Signature.objects.filter(Q(name__icontains=query) | Q(tsx_id__icontains=query))
    results_projects = [project for project in results_projects if check_view_permissions(request.user, project)]
    results_studies = [study for study in results_studies if check_view_permissions(request.user, study.project)]
    results_signatures = [sig for sig in results_signatures if check_view_permissions(request.user, sig.factor.assay.study.project)]

    results = {
        'projects_number' : len(results_projects),
        'studies_number' : len(results_studies),
        'signatures_number' : len(results_signatures),
        'projects': results_projects,
        'studies': results_studies,
        'signatures': results_signatures
    }
    return render(request, 'pages/ajax_search.html', {'statuss': results})

def graph_data(request):
    # Need to check permissions for entities

    query = request.GET.get('q')
    project = Project.objects.get(tsx_id=query)
    if not check_view_permissions(request.user, project):
        return JsonResponse({"data" : {}, "max_parallel":0, max_depth: "0"}, safe=False)
    studies = project.study_of.all()

    response = {
        'name': project.name,
        'type': 'project',
        'tsx_id': project.tsx_id,
        'view_url': project.get_absolute_url(),
        'create_url' : get_sub_create_url('project', project.tsx_id),
        'clone_url': reverse("projects:project_create") + "?clone=" + project.tsx_id
    }
    sign_count = 0
    study_count = 0
    assay_count = 0

    study_list = []
    for study in studies:
        assay_list = []
        for assay in study.assay_of.all():
            signature_list = []
            for factor in assay.factor_of.all():
                for signature in factor.signature_of_of.all():
                    sign_count +=1
                    signature_list.append({'name': signature.name, 'type': 'signature', 'tsx_id': signature.tsx_id, 'view_url': signature.get_absolute_url(),
                                          'create_url': {}, 'clone_url':""})
            assay_count +=1
            assay_list.append({'name': assay.name, 'children': signature_list, 'type': 'assay', 'tsx_id': assay.tsx_id, 'view_url': assay.get_absolute_url(),
                              'create_url': get_sub_create_url('assay', assay.tsx_id), 'clone_url':""})
        study_count +=1
        study_list.append({'name': study.name, 'children': assay_list, 'type': 'study', 'tsx_id': study.tsx_id, 'view_url': study.get_absolute_url(),
                          'create_url': get_sub_create_url('study', study.tsx_id), 'clone_url':""})
    response['children'] = study_list
    data = {
        "data": response,
        "max_parallel": max(assay_count, study_count, sign_count, 1),
        "max_depth": 4
    }

    return JsonResponse(data, safe=False)

def index(request):

    all_projects = Project.objects.all().order_by('id')
    projects = []
    studies = []
    assays = []
    signatures = []

    for project in all_projects:
        if check_view_permissions(request.user, project):
            # Might be better to loop around than to request.
            projects.append(project)
            studies = studies + [study for study in Study.objects.filter(project=project)]
            assays = assays + [ assay for assay in Assay.objects.filter(study__project=project)]
            signatures = signatures + [ signature for signature in Signature.objects.filter(factor__assay__study__project=project)]

    project_number = len(projects)
    paginator = Paginator(projects, 5)
    page = request.GET.get('projects')
    try:
        projects = paginator.page(page)
    except PageNotAnInteger:
        projects = paginator.page(1)
    except EmptyPage:
        projects = paginator.page(paginator.num_pages)

    study_number = len(studies)
    paginator = Paginator(studies, 6)
    page = request.GET.get('studies')
    try:
        studies = paginator.page(page)
    except PageNotAnInteger:
        studies = paginator.page(1)
    except EmptyPage:
        studies = paginator.page(paginator.num_pages)

    assay_number = len(assays)
    paginator = Paginator(assays, 6)
    page = request.GET.get('assays')
    try:
        assays = paginator.page(page)
    except PageNotAnInteger:
        assays = paginator.page(1)
    except EmptyPage:
        assays = paginator.page(paginator.num_pages)

    signature_number = len(signatures)
    paginator = Paginator(signatures, 6)
    page = request.GET.get('signatures')
    try:
        signatures = paginator.page(page)
    except PageNotAnInteger:
        signatures = paginator.page(1)
    except EmptyPage:
        signatures = paginator.page(paginator.num_pages)

    context = {
        'project_list': projects,
        'study_list': studies,
        'assay_list': assays,
        'signature_list': signatures,
        'project_number':project_number,
        'study_number': study_number,
        'assay_number': assay_number,
        'signature_number': signature_number
    }

    return render(request, 'pages/index.html', context)


def search(request,query):
    print(query)
    search_qs = Project.objects.filter(name__contains=query)

def get_sub_create_url(entity_type, tsx_id):

    if entity_type == 'project':
        return {'study': reverse('studies:study_create', kwargs={'prjid': tsx_id})}

    elif entity_type == 'study':
        return {'assay': reverse('assays:assay_create', kwargs={'stdid': tsx_id})}
    elif entity_type == 'assay':
        return {
            'factor': reverse('assays:factor_create', kwargs={'assid': tsx_id}),
            'signature': reverse('signatures:signature_create', kwargs={'assid': tsx_id})
        }


def render_403(request):
    if request.GET.get('edit'):
        action = "edit"
        split = request.GET.get('edit').split('/')
        type = split[1]
    elif request.GET.get('create'):
        action = "create"
        split = request.GET.get('create').split('/')
        type = split[1]
    else:
        action = "view"
        type = ""
    data = {
        'action': action,
        'type': type
    }

    return render(request, '403.html', {'data':data})
