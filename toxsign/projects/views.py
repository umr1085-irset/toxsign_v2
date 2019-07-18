from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.views.generic import DetailView, ListView, RedirectView, UpdateView, CreateView
from django.shortcuts import redirect
from guardian.mixins import PermissionRequiredMixin
from guardian.shortcuts import get_user_perms

from toxsign.assays.models import Assay
from toxsign.projects.models import Project
from toxsign.projects.forms import ProjectCreateForm
from toxsign.signatures.models import Signature
from toxsign.studies.models import Study


# TODO : clear 403 page redirect (page with an explanation?)
def DetailView(request, prjid):
    project_object = Project.objects.get(tsx_id=prjid)
    project = get_object_or_404(Project, pk=project_object.id)
    if not check_view_permissions(request.user, project):
        return redirect('/index')
    studies = project.study_of.all()
    assays = Assay.objects.filter(study__project=project)
    signatures = Signature.objects.filter(factor__assay__study__project=project)
    return render(request, 'projects/details.html', {'project': project,'studies': studies, 'assays': assays, 'signatures': signatures})

# TODO : clearer error message
class EditView(PermissionRequiredMixin, UpdateView):
    permission_required = 'change_project'

    model = Project
    template_name = 'projects/project_edit.html'
    fields = ["name", "description"]
    context_object_name = 'edit'

    def get_object(self, queryset=None):
        return Project.objects.get(pk=self.kwargs['pk'])

class CreateView(LoginRequiredMixin, CreateView):
    model = Project
    template_name = 'pages/entity_create.html'
    form_class = ProjectCreateForm

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
    elif user.is_authenticated and 'view_project' in get_user_perms(user, project):
        has_access = True

    return has_access
