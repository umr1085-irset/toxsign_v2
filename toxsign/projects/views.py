from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.views.generic import DetailView, ListView, RedirectView, UpdateView, CreateView
from django.shortcuts import redirect
from guardian.mixins import PermissionRequiredMixin
from guardian.shortcuts import get_perms


from toxsign.assays.models import Assay, Factor
from toxsign.projects.models import Project
from toxsign.projects.forms import ProjectCreateForm
from toxsign.signatures.models import Signature
from toxsign.studies.models import Study


# TODO : clear 403 page redirect (page with an explanation?)
def DetailView(request, prjid):
    project_object = Project.objects.get(tsx_id=prjid)
    project = get_object_or_404(Project, pk=project_object.id)
    if not check_view_permissions(request.user, project):
        return redirect('/unauthorized')
    studies = project.study_of.all()
    assays = Assay.objects.filter(study__project=project)
    factors = Factor.objects.filter(assay__study__project=project)
    signatures = Signature.objects.filter(factor__assay__study__project=project)
    return render(request, 'projects/details.html', {'project': project,'studies': studies, 'assays': assays, 'factors': factors, 'signatures': signatures})

# TODO : clear 403 page redirect (page with an explanation?)
class EditView(PermissionRequiredMixin, UpdateView):
    permission_required = 'change_project'
    model = Project
    login_url = "/unauthorized"
    redirect_field_name="edit"
    template_name = 'projects/project_edit.html'
    fields = ["name", "description"]
    context_object_name = 'edit'

    def get_object(self, queryset=None):
        return Project.objects.get(pk=self.kwargs['pk'])

class CreateProjectView(LoginRequiredMixin, CreateView):
    model = Project
    template_name = 'projects/entity_create.html'
    form_class = ProjectCreateForm

    def get_form_kwargs(self):
        kwargs = super(CreateView, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
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
        self.object.created_by = self.request.user
        return super(CreateView, self).form_valid(form)

def check_view_permissions(user, project):
    has_access = False
    if project.status == "PUBLIC":
        has_access = True
    elif user.is_superuser:
        has_access = True
    elif user.is_authenticated and 'view_project' in get_perms(user, project):
        has_access = True

    return has_access

def check_edit_permissions(user, project):
    has_access = False
    if user.is_superuser:
        has_access = True
    elif user.is_authenticated and 'change_project' in get_perms(user, project):
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

