import json, os

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.views import generic
from django.views.generic import DetailView, ListView, RedirectView, UpdateView
from django.http import HttpResponse, JsonResponse
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger, Page
from django.conf import settings


from toxsign.superprojects.models import Superproject
from toxsign.assays.models import Assay, Factor
from toxsign.projects.models import Project
from toxsign.signatures.models import Signature
from toxsign.jobs.models import Job
from toxsign.projects.views import check_view_permissions, check_edit_permissions

from toxsign.superprojects.documents import SuperprojectDocument
from toxsign.projects.documents import ProjectDocument
from toxsign.assays.documents import AssayDocument
from toxsign.signatures.documents import SignatureDocument
from toxsign.ontologies.documents import *
from elasticsearch_dsl import Q as Q_es

from django.template.loader import render_to_string
from . import forms
from django.http import JsonResponse
from django.http import FileResponse
from django.utils.functional import LazyObject

class SearchResults(LazyObject):
    def __init__(self, search_object):
        self._wrapped = search_object

    def __len__(self):
        return self._wrapped.count()

    def __getitem__(self, index):
        search_results = self._wrapped[index]
        if isinstance(index, slice):
            search_results = list(search_results)
        return search_results

def HomeView(request):
        context = {}
        return render(request, 'pages/home.html',context)

def download_signature(request, sigid):
    from toxsign.scripts.processing import zip_results
    sig = get_object_or_404(Signature, tsx_id=sigid)
    if not check_view_permissions(request.user, sig.factor.assay.project):
        return redirect('/unauthorized')

    sig_folder = "{}/files/{}/{}/{}/{}/".format(settings.MEDIA_ROOT, sig.factor.assay.project.tsx_id, sig.factor.assay.tsx_id, sig.factor.tsx_id, sig.tsx_id)
    if not os.path.exists(sig_folder + 'archive.zip'):
        zip_results(sig_folder)

    response = FileResponse(open(sig_folder +'archive.zip', 'rb'))
    response['Content-Type'] = "application/zip"
    response['Content-Disposition'] = 'attachment; filename={}_archive.zip'.format(sig.tsx_id)
    response['Content-Transfer-Encoding'] = "binary"
    response['Content-Length'] = os.path.getsize(sig_folder +'archive.zip')

    return response


def download_job_result(request, jobid):
    from toxsign.scripts.processing import zip_results
    job = get_object_or_404(Job, id=jobid)
    if not job.created_by == request.user:
         return redirect('/unauthorized')

    if not job.results or not 'archive' in job.results or not job.results['archive']:
        return redirect('/unauthorized')

    archive_file = job.results['archive']
    response = FileResponse(open(archive_file, 'rb'))
    response['Content-Type'] = "application/zip"
    response['Content-Disposition'] = 'attachment; filename=job_{}_results.zip'.format(job.title)
    response['Content-Transfer-Encoding'] = "binary"
    response['Content-Length'] = os.path.getsize(archive_file)

    return response

def autocompleteModel(request):
    query = request.GET.get('q')

    try:
        # Wildcard for search (not optimal)
        query = "*" + query + "*"
        if request.user.is_authenticated:
            if request.user.is_superuser:
                q = Q_es()
            else:
                groups = [group.id for group in request.user.groups.all()]
                q = Q_es("match", created_by__username=request.user.username)  | Q_es("match", status="PUBLIC") | Q_es('nested', path="read_groups", query=Q_es("terms", read_groups__id=groups))
        else:
            q = Q_es("match", status="PUBLIC")

        allowed_projects =  ProjectDocument.search().sort('id').query(q).scan()
        # Limit all query to theses projects
        allowed_projects_id_list = [project.id for project in allowed_projects]

        # Now do the queries
        results_superprojects = SuperprojectDocument.search().sort('id')
        results_signatures = SignatureDocument.search().sort('id').filter("terms", factor__assay__project__id=allowed_projects_id_list)
        # This search in all fields.. might be too much. Might need to restrict to fields we actually show on the search page..
        q1 = Q_es("query_string", query=query)

        results_superprojects = paginate(results_superprojects.filter(q1), request.GET.get('superprojects'), 5, True)
        results_projects = paginate(ProjectDocument.search().query(q & q1), request.GET.get('projects'), 5, True)
        results_signatures = paginate(results_signatures.filter(q1), request.GET.get('signatures'), 5, True)

    # Fallback to DB search
    # Need to select the correct error I guess
    except Exception as e:

        results_superprojects = paginate(Superproject.objects.filter(Q(name__icontains=query) | Q(description__icontains=query) | Q(tsx_id__icontains=query)), request.GET.get('superprojects'), 5)
        results_projects = Project.objects.filter(Q(name__icontains=query) | Q(description__icontains=query) | Q(tsx_id__icontains=query))
        results_signatures = Signature.objects.filter(Q(name__icontains=query) | Q(tsx_id__icontains=query))

        results_projects = paginate([project for project in results_projects if check_view_permissions(request.user, project)], request.GET.get('projects'), 5)
        results_signatures = paginate([sig for sig in results_signatures if check_view_permissions(request.user, sig.factor.assay.project)], request.GET.get('signatures'), 5)

    is_active = {'superproject': "", 'project': "", 'signature': ""}
    # If a specific page was requested,  set the related tab to active
    if request.GET.get('projects') or request.GET.get('assays') or request.GET.get('signatures'):

        if request.GET.get('projects'):
            is_active['project'] = "active"
        elif request.GET.get('superprojects'):
            is_active['superproject'] = "active"
        elif request.GET.get('signatures'):
            is_active['signature'] = "active"
    else:
    # Set the first non empty tab to active (Else, superproject)
        if results_superprojects.paginator.count:
            is_active['superproject'] = "active"
        elif results_projects.paginator.count:
            is_active['project'] = "active"
        elif results_signatures.paginator.count:
            is_active['signature'] = "active"
        else:
            is_active['superproject'] = "active"

    results = {
        'superprojects' : results_superprojects,
        'projects': results_projects,
        'signatures': results_signatures,
        'is_active': is_active,
        'query': request.GET.get('q')
    }
    return render(request, 'pages/ajax_search.html', {'status': results})

def advanced_search_form(request):

    if request.method == 'POST':
        data = request.POST
        terms = json.loads(data['terms'])
        entity = data['entity']
        context = {}
        data = {}
        if entity == 'project':
            context['projects'] = search(request, Project, ProjectDocument, entity, terms)

        elif entity == "signature":
            context['signatures'] = search(request, Signature, SignatureDocument, entity, terms)


        data['html_page'] = render_to_string('pages/partial_advanced_search.html',
            context,
            request=request,
        )
        return JsonResponse(data)

    else:
        entity_type = request.GET.get('entity')
        data = {}
        if entity_type == 'project':
            form = forms.ProjectSearchForm()
        elif entity_type == 'signature':
            form = forms.SignatureSearchForm()

        context = {'form': form}
        data['html_form'] = render_to_string('pages/advanced_search_form.html',
            context,
            request=request,
        )
        return JsonResponse(data)

    return None

def graph_data(request):

    query = request.GET.get('q')
    project = Project.objects.get(tsx_id=query)
    if not check_view_permissions(request.user, project):
        return JsonResponse({"data" : {}, "max_parallel":0, max_depth: "0"}, safe=False)

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
    assay_count = 0
    factor_count = 0

    assay_list = []
    for assay in project.assay_of.all():
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
                          'edit_url': get_edit_url('factor', factor.tsx_id), 'editable': editable, 'self_editable': editable,
                          'count_subentities': count_subentities(factor, 'factor'),
                          'subentities': [{'name' : 'subfactors', 'is_modal': True,
                            'view_url': reverse('assays:factor_subfactor_detail', kwargs={'facid': factor.tsx_id})}]})
        assay_count +=1
        assay_list.append({'name': assay.name, 'children': factor_list, 'type': 'assay', 'tsx_id': assay.tsx_id, 'view_url': assay.get_absolute_url(),
                          'create_url': get_sub_create_url('assay', project.tsx_id, assay.tsx_id),
                          'clone_url': get_clone_url('assay', project.tsx_id, assay.tsx_id),
                          'edit_url': get_edit_url('assay', assay.tsx_id), 'editable': editable, 'self_editable': editable})

    response['children'] = assay_list

    data = {
        "data": response,
        "max_parallel": max(assay_count, sign_count, 1),
        "max_depth": 4
    }

    return JsonResponse(data, safe=False)

def index(request):

    try:
        if request.user.is_authenticated:
            if request.user.is_superuser:
                q = Q_es()
            else:
                groups = [group.id for group in request.user.groups.all()]
                q = Q_es("match", created_by__username=request.user.username)  | Q_es("match", status="PUBLIC") | Q_es('nested', path="read_groups", query=Q_es("terms", read_groups__id=groups))
        else:
            q = Q_es("match", status="PUBLIC")

        allowed_projects =  ProjectDocument.search().sort('id').query(q).scan()
        allowed_projects_id_list = [project.id for project in allowed_projects]

        superprojects = SuperprojectDocument.search()
        assays = AssayDocument.search().sort('id').filter("terms", project__id=allowed_projects_id_list)
        signatures = SignatureDocument.search().sort('id').filter("terms", factor__assay__project__id=allowed_projects_id_list)

        # Since ES search objects are generators, we need to re-query them
        projects = paginate(ProjectDocument.search().sort('id').query(q), request.GET.get('projects'), 5, True)
        superprojects = paginate(superprojects, request.GET.get('superprojects'), 5, True)
        assays = paginate(assays, request.GET.get('assays'), 5, True)
        signatures = paginate(signatures, request.GET.get('signatures'), 5, True)

    except Exception as e:
        raise e
        superprojects = Superproject.objects.all()
        all_projects = Project.objects.all().order_by('id')
        projects = []
        assays = []
        signatures = []
        for project in all_projects:
            if check_view_permissions(request.user, project):
                # Might be better to loop around than to request.
                projects.append(project)
            assays = assays + [ assay for assay in Assay.objects.filter(project=project)]
            signatures = signatures + [ signature for signature in Signature.objects.filter(factor__assay__project=project)]

        superprojects = paginate(superprojects, request.GET.get('superprojects'), 5)
        projects = paginate(projects, request.GET.get('projects'), 5)
        assays = paginate(assays, request.GET.get('assays'), 5)
        signatures = paginate(signatures, request.GET.get('signatures'), 5)

    is_active = {'superproject': "", 'project': "", 'assay': "", 'signature': ""}
    # If a specific page was requested,  set the related tab to active
    if request.GET.get('projects') or request.GET.get('assays') or request.GET.get('signatures'):

        if request.GET.get('projects'):
            is_active['project'] = "active"
        elif request.GET.get('assays'):
            is_active['assay'] = "active"
        elif request.GET.get('superprojects'):
            is_active['superproject'] = "active"
        elif request.GET.get('signatures'):
            is_active['signature'] = "active"
    else:
    # Set the first non empty tab to active (Else, superproject)
        if superprojects.paginator.count:
            is_active['superproject'] = "active"
        elif projects.paginator.count:
            is_active['project'] = "active"
        elif assays.paginator.count:
            is_active['project'] = "active"
        elif signatures.paginator.count:
            is_active['signature'] = "active"
        else:
            is_active['superproject'] = "active"

    context = {
        'superproject_list': superprojects,
        'project_list': projects,
        'assay_list': assays,
        'signature_list': signatures,
        "is_active": is_active
    }

    return render(request, 'pages/index.html', context)

def get_sub_create_url(entity_type, prj_id, tsx_id):

    query = "?selected=" + tsx_id

    if entity_type == 'project':
        return {'assay': reverse('assays:assay_create', kwargs={'prjid': prj_id}) + query}
    elif entity_type == 'assay':
        return {'factor': reverse('assays:factor_create', kwargs={'prjid': prj_id}) + query}
    elif entity_type == 'factor':
        return {'signature': reverse('signatures:signature_create', kwargs={'prjid': prj_id}) + query}

def get_clone_url(entity_type, prj_id, tsx_id):

    query = "?clone=" + tsx_id

    if entity_type == 'project':
        return reverse('projects:project_create') + query
    elif entity_type == 'assay':
        return reverse('assays:assay_create', kwargs={'prjid': prj_id}) + query
    elif entity_type == 'factor':
        return reverse('assays:factor_create', kwargs={'prjid': prj_id}) + query
    elif entity_type == 'signature':
        return reverse('signatures:signature_create', kwargs={'prjid': prj_id}) + query

def get_edit_url(entity_type, tsx_id):

    if entity_type == 'project':
        return reverse('projects:project_edit', kwargs={'prjid': tsx_id})
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

def search(request, model, document, entity, search_terms):

    # First try with elasticsearch, then fallback to  DB query if it fails
    try:
        # Wildcard for search
        if request.user.is_authenticated:
            if request.user.is_superuser:
                q = Q_es()
            else:
                groups = [group.id for group in request.user.groups.all()]
                q = Q_es("match", created_by__username=request.user.username)  | Q_es("match", status="PUBLIC") | Q_es('nested', path="read_groups", query=Q_es("terms", read_groups__id=groups))
        else:
            q = Q_es("match", status="PUBLIC")

        allowed_projects =  ProjectDocument.search().query(q)
        # Limit all query to theses projects
        allowed_projects_id_list = [project.id for project in allowed_projects]

        query = generate_query(search_terms)
        # Now do the queries
        if entity == 'project':
            results = allowed_projects
        elif entity == "signature":
            results = SignatureDocument.search().filter("terms", factor__assay__project__id=allowed_projects_id_list)

        if query:
            results = results.filter(query)

        return results

    except Exception as e:
        raise e

def generate_query(search_terms):

    # Need a dict to link the fields to the correct document
    documentDict = {
        "biological": BiologicalDocument,
        "cellline": CellLineDocument,
        "cell": CellDocument,
        "chemical": ChemicalDocument,
        "disease": DiseaseDocument,
        "experiment": ExperimentDocument,
        "organism": SpeciesDocument,
        "tissue": TissueDocument
    }

    for index, item in enumerate(search_terms):
            # TODO : Refactor
            if index == 0:
                # Couldn't make double nested query work, so first query the correct ontologies, then query the correct signatures
                if item['is_ontology']:
                    if item['ontology_options']['search_type'] == "CHILDREN":
                        q = Q_es("match", id=item['ontology_options']['id'])
                        children_list =  [ontology.as_children for ontology in documentDict[item['arg_type']].search().query(q)][0].split(",")
                        onto_query = q | Q_es("terms", onto_id=children_list)
                    else:
                        onto_query = Q_es("match", id=item['ontology_options']['id'])

                    ontology_list = [ontology.id for ontology in documentDict[item['arg_type']].search().query(onto_query).scan()]
                    id_field = item['arg_type'] + "__id"
                    query = Q_es("nested", path=item['arg_type'], query=Q_es("terms", **{id_field:ontology_list}))

                else:
                    query = Q_es("wildcard", **{item['arg_type']:item['arg_value']})
            else:
                if item['is_ontology']:
                    if item['ontology_options']['search_type'] == "CHILDREN":
                        q = Q_es("match", id=item['ontology_options']['id'])
                        children_list =  [ontology.as_children for ontology in documentDict[item['arg_type']].search().query(q)][0].split(",")
                        onto_query = q | Q_es("terms", onto_id=children_list)
                    else:
                        onto_query = Q_es("match", id=item['ontology_options']['id'])

                    ontology_list = [ontology.id for ontology in documentDict[item['arg_type']].search().query(onto_query).scan()]
                    id_field = item['arg_type'] + "__id"
                    new_query = Q_es("nested", path=item['arg_type'], query=Q_es("terms", **{id_field:ontology_list}))

                else:
                    new_query = Q_es("wildcard", **{item['arg_type']:item['arg_value']})

                if item['bool_type'] == "AND":
                    query = query & new_query
                else:
                    query = query | new_query
    return query

def count_subentities(entity, entity_type):
    # Might use it for other entity types later on
    count = 0
    if entity_type == "factor":
        count += entity.chemical_subfactor_of.count()
    return count

def paginate(values, query=None, count=5, is_ES=False):

    if is_ES:
        paginator = Paginator(SearchResults(values), count)
    else:
        paginator = Paginator(values, count)

    try:
        val = paginator.page(query)
    except PageNotAnInteger:
        val = paginator.page(1)
    except EmptyPage:
        val = paginator.page(paginator.num_pages)

    return val
