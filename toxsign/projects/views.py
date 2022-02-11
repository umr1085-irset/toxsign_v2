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
from toxsign.assays.models import Assay, Factor
from toxsign.projects.models import Project
from toxsign.projects.forms import ProjectCreateForm, ProjectEditForm
from toxsign.signatures.models import Signature
from toxsign.superprojects.models import Superproject

from django.core.mail import mail_admins

# TODO : clear 403 page redirect (page with an explanation?)
def DetailView(request, prjid):
    project = get_object_or_404(Project, tsx_id=prjid)
    if not check_view_permissions(request.user, project):
        return redirect('/unauthorized')
    assays = Assay.objects.filter(project=project)
    factors = Factor.objects.filter(assay__project=project)
    signatures = Signature.objects.filter(factor__assay__project=project)
    return render(request, 'projects/details.html', {'project': project, 'assays': assays, 'factors': factors, 'signatures': signatures})

# TODO : clear 403 page redirect (page with an explanation?)
class EditProjectView(PermissionRequiredMixin, UpdateView):
    # Only owner has delete_project perm
    permission_required = ['change_project', 'delete_project']
    model = Project
    login_url = "/unauthorized"
    redirect_field_name="edit"
    form_class = ProjectEditForm
    template_name = 'projects/project_edit.html'
    context_object_name = 'edit'

    def get_form_kwargs(self):
        kwargs = super(EditProjectView, self).get_form_kwargs()
        superprojects = Superproject.objects.filter(created_by=self.request.user)
        kwargs.update({'user': self.request.user, 'superprojects': superprojects})
        return kwargs

    def get_object(self, queryset=None):
        project = Project.objects.get(tsx_id=self.kwargs['prjid'])
        if project.status == "PUBLIC":
            return None
        else:
            return project


class CreateProjectView(LoginRequiredMixin, CreateView):
    model = Project
    template_name = 'projects/entity_create.html'
    form_class = ProjectCreateForm

    def get_form_kwargs(self):
        kwargs = super(CreateProjectView, self).get_form_kwargs()
        superprojects = Superproject.objects.filter(created_by=self.request.user)
        kwargs.update({'user': self.request.user, 'superprojects': superprojects})
        if self.request.GET.get('clone'):
            projects = Project.objects.filter(tsx_id=self.request.GET.get('clone'))
            if projects.exists():
                project = projects.first()
                if check_view_permissions(self.request.user, project):
                    kwargs.update({'project': project})
        return kwargs

    # Autofill the user
    def form_valid(self, form):
        self.object = form.save(commit=False)
        # self.request.user is not a 'true' user, so it bugs out in elasticsearch...
        self.object.created_by = get_user(self.request)
        return super(CreateProjectView, self).form_valid(form)

def publicize_project(request, prjid):

    project = Project.objects.get(tsx_id=prjid)
    if not project.status == "PRIVATE":
        return redirect(reverse("projects:detail", kwargs={"prjid": prjid}))

    if not request.user == project.created_by:
        return redirect('/unauthorized')

    data = dict()
    if request.method == 'POST':
        project.status = "PENDING"
        project.save()
        body = "User {} requested project {} to be publicized. Project is in pending state.".format(project.created_by, project.tsx_id)
        mail_admins("Project publicize request : " + project.tsx_id, body)
        data['redirect'] = reverse("projects:detail", kwargs={"prjid": prjid})
        data['form_is_valid'] = True
    else:
       context = {'project': project}
       data['html_form'] = render_to_string('projects/partial_project_public.html',
           context,
           request=request,
       )
    return JsonResponse(data)

def check_view_permissions(user, project, strict=False, allow_superuser=True):
    has_access = False
    if project.status == "PUBLIC" and not strict:
        has_access = True
    elif allow_superuser and user.is_superuser:
        has_access = True
    elif user.is_authenticated and 'view_project' in get_perms(user, project):
        has_access = True

    return has_access

def check_edit_permissions(user, project, need_owner=False):
    has_access = False

    if not need_owner:
        if user.is_authenticated and 'change_project' in get_perms(user, project) and not need_owner:
            has_access = True
    else:
        if user == project.created_by:
            has_access = True

    # Stop modification when public
    if project.status == "PUBLIC":
        has_access = False

    if user.is_superuser:
        has_access = True

    return has_access


def get_access_type(user, project):
    access = {
        'view' : False,
        'edit': False,
        'delete': False
    }

    if user.is_authenticated:
        perms = get_perms(user, project)
        if 'view_project' in perms:
            access['view'] = True
        if 'change_project' in perms:
            access['edit'] = True
        if 'delete_project' in perms:
            access['delete'] = True

    if project.status == "PUBLIC":
        access['view'] = True

    return access
