from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.views import generic
from django.views.generic import CreateView, DetailView, ListView, RedirectView, UpdateView
from django.contrib.auth.decorators import login_required

from guardian.mixins import PermissionRequiredMixin

from toxsign.projects.models import Project
from toxsign.studies.models import Study
from toxsign.signatures.models import Signature

from toxsign.projects.views import check_view_permissions
from toxsign.studies.forms import StudyCreateForm

def DetailView(request, stdid):

    study = get_object_or_404(Study, tsx_id=stdid)
    project = study.project
    if not check_view_permissions(request.user, project):
        return redirect('/index')

    assays = study.assay_of.all()
    signatures = Signature.objects.filter(factor__assay__study=study)
    return render(request, 'studies/details.html', {'project': project,'study': study, 'assays': assays, 'signatures': signatures})

# TODO : check for project edit permission
class EditView(PermissionRequiredMixin, UpdateView):

    permission_required = 'change_project'

    model = Study
    template_name = 'studies/study_edit.html'
    fields = ["name", "description"]
    context_object_name = 'edit'

    def get_permission_object(self):
        study = Study.objects.get(pk=self.kwargs['pk'])
        project = study.project
        return project

    def get_object(self, queryset=None):
        return Study.objects.get(pk=self.kwargs['pk'])

class CreateView(LoginRequiredMixin, CreateView):
    model = Study
    template_name = 'pages/entity_create.html'
    form_class = StudyCreateForm

    # Autofill the user and project
    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.created_by = self.request.user
        project = Project.objects.get(tsx_id=self.kwargs['prjid'])
        # Need safegards (access? exists?)
        self.object.project = project
        return super(CreateView, self).form_valid(form)
