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
from toxsign.projects.views import check_view_permissions, check_edit_permissions

from toxsign.projects.documents import ProjectDocument
from toxsign.studies.documents import StudyDocument
from toxsign.signatures.documents import SignatureDocument
from elasticsearch_dsl import Q as Q_es

from django.template.loader import render_to_string
from . import forms
from django.http import JsonResponse


def HomeView(request):
        context = {}
        return render(request, 'pages/home.html',context)

def autocompleteModel(request):
    query = request.GET.get('q')

    try:
        # Wildcard for search
        query = "*" + query + "*"
        if request.user.is_authenticated:
            groups = [group.id for group in request.user.groups.all()]
            q = Q_es('nested', path="read_groups", query=Q_es("terms", read_groups__id=groups)) | Q_es("match", status="PUBLIC")
        else:
            q = Q_es("match", status="PUBLIC")

        allowed_projects =  ProjectDocument.search().query(q).scan()
        # Limit all query to theses projects
        allowed_projects_id_list = [project.id for project in allowed_projects]

        # Now do the queries

        results_projects = ProjectDocument.search().filter("terms", id=allowed_projects_id_list)
        results_studies = StudyDocument.search().filter("terms", project__id=allowed_projects_id_list)
        results_signatures = SignatureDocument.search().filter("terms", factor__assay__study__project__id=allowed_projects_id_list)

        # This search in all fields.. might be too much. Might need to restrict to fields we actually show on the search page..
        q = Q_es("query_string", query=query+"*")

        results_projects = results_projects.filter(q)
        projects_number = results_projects.count()
        results_projects = results_projects.scan()

        results_studies = results_studies.filter(q)
        studies_number = results_studies.count()
        results_studies = results_studies.scan()

        results_signatures = results_signatures.filter(q)
        signatures_number = results_signatures.count()
        results_signatures = results_signatures.scan()

    # Fallback to DB search
    # Need to select the correct error I guess
    except Exception as e:
        results_projects = Project.objects.filter(Q(name__icontains=query) | Q(description__icontains=query) | Q(tsx_id__icontains=query))
        results_studies = Study.objects.filter(Q(name__icontains=query) | Q(description__icontains=query) | Q(tsx_id__icontains=query))
        results_signatures = Signature.objects.filter(Q(name__icontains=query) | Q(tsx_id__icontains=query))

        results_projects = [project for project in results_projects if check_view_permissions(request.user, project)]
        results_studies = [study for study in results_studies if check_view_permissions(request.user, study.project)]
        results_signatures = [sig for sig in results_signatures if check_view_permissions(request.user, sig.factor.assay.study.project)]
        projects_number =  len(results_projects)
        studies_number = len(results_studies)
        signatures_number = len(results_signatures)

    results = {
        'projects_number' : projects_number,
        'studies_number' : studies_number,
        'signatures_number' : signatures_number,
        'projects': results_projects,
        'studies': results_studies,
        'signatures': results_signatures
    }
    return render(request, 'pages/ajax_search.html', {'statuss': results})

def advanced_search_form(request):

    if request.method == 'POST':
        data = request.POST
        terms = json.loads(data['terms'])
        entity = data['entity']
    else:
        entity_type = request.GET.get('entity')
        data = {}
        if entity_type == 'project':
        # Manually selecting the fields might be better
        # Should be done in the form directly maybe
            field_names = ['name', 'tsx_id', 'description']
            form = forms.ProjectSearchForm(fields=field_names)
            context = {'form': form, 'field_names': field_names}
            data['html_form'] = render_to_string('pages/advanced_search_form.html',
                context,
                request=request,
            )
            return JsonResponse(data)
        elif entity_type == 'study':
            pass
        elif entity_type == 'signature':
            pass
    return None

def graph_data(request):

    query = request.GET.get('q')
    project = Project.objects.get(tsx_id=query)
    if not check_view_permissions(request.user, project):
        return JsonResponse({"data" : {}, "max_parallel":0, max_depth: "0"}, safe=False)
    studies = project.study_of.all()

    editable = check_edit_permissions(request.user, project)

    response = {
        'name': project.name,
        'type': 'project',
        'tsx_id': project.tsx_id,
        'view_url': project.get_absolute_url(),
        'create_url': get_sub_create_url('project', project.tsx_id, project.tsx_id),
        'edit_url': get_edit_url('project', project.tsx_id),
        'clone_url': get_clone_url('project', project.tsx_id, project.tsx_id),
        'self_editable': check_edit_permissions(request.user, project, True),
        'editable': editable
    }
    sign_count = 0
    study_count = 0
    assay_count = 0
    factor_count = 0

    study_list = []
    for study in studies:
        assay_list = []
        for assay in study.assay_of.all():
            factor_list = []
            for factor in assay.factor_of.all():
                signature_list = []
                for signature in factor.signature_of_of.all():
                    sign_count +=1
                    signature_list.append({'name': signature.name, 'type': 'signature', 'tsx_id': signature.tsx_id, 'view_url': signature.get_absolute_url(),
                                          'create_url': {}, 'clone_url': get_clone_url('signature', project.tsx_id, signature.tsx_id),
                                          'edit_url': get_edit_url('signature', signature.tsx_id), 'editable': editable, 'self_editable': editable})
                factor_count += 1
                factor_list.append({'name': factor.name, 'children': signature_list, 'type': 'factor', 'tsx_id': factor.tsx_id, 'view_url': factor.get_absolute_url(),
                              'create_url': get_sub_create_url('factor', project.tsx_id, factor.tsx_id),
                              'clone_url': get_clone_url('factor', project.tsx_id, factor.tsx_id),
                              'edit_url': get_edit_url('factor', factor.tsx_id), 'editable': editable, 'self_editable': editable})
            assay_count +=1
            assay_list.append({'name': assay.name, 'children': factor_list, 'type': 'assay', 'tsx_id': assay.tsx_id, 'view_url': assay.get_absolute_url(),
                              'create_url': get_sub_create_url('assay', project.tsx_id, assay.tsx_id),
                              'clone_url': get_clone_url('assay', project.tsx_id, assay.tsx_id),
                              'edit_url': get_edit_url('assay', assay.tsx_id), 'editable': editable, 'self_editable': editable})
        study_count +=1
        study_list.append({'name': study.name, 'children': assay_list, 'type': 'study', 'tsx_id': study.tsx_id, 'view_url': study.get_absolute_url(),
                          'create_url': get_sub_create_url('study', project.tsx_id, study.tsx_id),
                          'clone_url': get_clone_url('study', project.tsx_id, study.tsx_id),
                          'edit_url': get_edit_url('study', study.tsx_id), 'editable': editable, 'self_editable': editable})
    response['children'] = study_list

    data = {
        "data": response,
        "max_parallel": max(assay_count, study_count, sign_count, 1),
        "max_depth": 5
    }

    return JsonResponse(data, safe=False)

def index(request):

    all_projects = Project.objects.all().order_by('id')
    projects = []
    studies = []
    assays = []
    signatures = []

    # TODO (Maybe?) -> Show index from elasticsearch : need fallback
    # Below : tentative implementation for projects and studies

    #  !!!!! WARNING: 'terms' query does not work on tsx_id fields (it works on id fields) !!!!!

    #if request.user.is_authenticated:
    #    groups = [group.id for group in request.user.groups.all()]
    #    q = Q_es('nested', path="read_groups", query=Q_es("terms", read_groups__id=groups)) | Q_es("match", status="PUBLIC")
    #else:
    #    q = Q_es("match", status="PUBLIC")
        # Should use ES for pagination..
        # Need to convert it to list for it to work with paginator...
    #project_list =  ProjectDocument.search().query(q).scan()
    #project_id_list = []
    #for project in project_list:
    #    projects.append(project)
    #    project_id_list.append(project.id)
    #q = Q_es("terms", project__id=project_id_list)
    #studies = StudyDocument().search().query(q).scan()
    #studies = [study for study in studies]

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

def get_sub_create_url(entity_type, prj_id, tsx_id):
    query = "?selected=" + tsx_id

    if entity_type == 'project':
        return {'study': reverse('studies:study_create', kwargs={'prjid': prj_id}) + query}
    elif entity_type == 'study':
        return {'assay': reverse('assays:assay_create', kwargs={'prjid': prj_id}) + query}
    elif entity_type == 'assay':
        return {'factor': reverse('assays:factor_create', kwargs={'prjid': prj_id}) + query}
    elif entity_type == 'factor':
        return {'signature': reverse('signatures:signature_create', kwargs={'prjid': prj_id}) + query}

def get_clone_url(entity_type, prj_id, tsx_id):

    query = "?clone=" + tsx_id

    if entity_type == 'project':
        return reverse('projects:project_create') + query
    elif entity_type == 'study':
        return reverse('studies:study_create', kwargs={'prjid': prj_id}) + query
    elif entity_type == 'assay':
        return reverse('assays:assay_create', kwargs={'prjid': prj_id}) + query
    elif entity_type == 'factor':
        return reverse('assays:factor_create', kwargs={'prjid': prj_id}) + query
    elif entity_type == 'signature':
        return reverse('signatures:signature_create', kwargs={'prjid': prj_id}) + query

def get_edit_url(entity_type, tsx_id):

    if entity_type == 'project':
        return reverse('projects:project_edit', kwargs={'prjid': tsx_id})
    elif entity_type == 'study':
        return reverse('studies:study_edit', kwargs={'stdid': tsx_id})
    elif entity_type == 'assay':
        return reverse('assays:assay_edit', kwargs={'assid': tsx_id})
    elif entity_type == 'factor':
        return reverse('assays:factor_edit', kwargs={'facid': tsx_id})
    elif entity_type == 'signature':
        return reverse('signatures:signature_edit', kwargs={'sigid': tsx_id})

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
