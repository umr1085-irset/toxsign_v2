from django.contrib.auth import get_user_model, get_user
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.views.generic import DetailView, ListView, RedirectView, UpdateView, CreateView
from django.shortcuts import redirect
from guardian.mixins import PermissionRequiredMixin
from guardian.shortcuts import get_perms

from django.template.loader import render_to_string
from django.http import JsonResponse

from toxsign.superprojects.forms import SuperprojectEditForm, SuperprojectCreateForm
from toxsign.projects.models import Project
from toxsign.superprojects.models import Superproject
from toxsign.projects.views import check_view_permissions

# TODO : clear 403 page redirect (page with an explanation?)
def DetailView(request, spjid):
    superproject = get_object_or_404(Superproject, tsx_id=spjid)
    raw_projects = superproject.project_of.all()
    projects = []
    for project in raw_projects:
        dict = {'name': project.name, 'description': project.description, 'tsx_id': project.tsx_id, 'created_at': project.created_at, 'created_by': project.created_by, 'visible': False}
        if check_view_permissions(request.user, project):
            dict['visible'] = True
        projects.append(dict)

    return render(request, 'superprojects/details.html', {'superproject': superproject, 'projects': projects})

def edit_superproject(request, spjid):
    if not request.user.is_authenticated:
        redirect('/unauthorized')

    superproject = get_object_or_404(Superproject, tsx_id=spjid)

    if not request.user == superproject.created_by:
        redirect('/unauthorized')

    data = {}
    if request.method == 'POST':
        form = SuperprojectEditForm(request.POST, instance=superproject)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.save()
            data['redirect'] = reverse("superprojects:detail", kwargs={"spjid": obj.tsx_id})
            data['form_is_valid'] = True
        else:
            data['form_is_valid'] = False
    else:
        form = SuperprojectCreateForm(instance=superproject)

    context = {'form': form}
    data['html_form'] = render_to_string('superprojects/partial_superproject_edit.html',
        context,
        request=request,
    )
    return JsonResponse(data)


def create_superproject(request):

    if not request.user.is_authenticated:
        redirect('/unauthorized')

    data = {}
    if request.method == 'POST':
        form = SuperprojectCreateForm(request.POST)
        if form.is_valid():
            object = form.save(commit=False)
            object.created_by = get_user(request)
            object.save()
            data['redirect'] = reverse("superprojects:detail", kwargs={"spjid": object.tsx_id})
            data['form_is_valid'] = True
        else:
            data['form_is_valid'] = False
    else:
        form = SuperprojectCreateForm()

    context = {'form': form}
    data['html_form'] = render_to_string('superprojects/partial_superproject_create.html',
        context,
        request=request,
    )
    return JsonResponse(data)

def unlink_project(request, spjid, prjid):
    if not request.user.is_authenticated:
        redirect('/unauthorized')

    superproject = get_object_or_404(Superproject, tsx_id=spjid)

    if not request.user == superproject.created_by:
        redirect('/unauthorized')

    project = get_object_or_404(Project, tsx_id=prjid)

    data = {}
    context = {'superproject': superproject, 'project' : project}
    if request.method == 'POST':
        project.superproject = None
        project.save()
        data['form_is_valid'] = True
        data['redirect'] = reverse("superprojects:detail", kwargs={"spjid": superproject.tsx_id})

    data['html_form'] = render_to_string('superprojects/partial_superproject_project_remove.html',
        context,
        request=request,
    )
    return JsonResponse(data)
