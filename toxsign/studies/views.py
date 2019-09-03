from django.contrib.auth import get_user
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
from toxsign.assays.models import Factor
from toxsign.signatures.models import Signature

from toxsign.projects.views import check_view_permissions
from toxsign.studies.forms import StudyCreateForm, StudyEditForm

def DetailView(request, stdid):

    study = get_object_or_404(Study, tsx_id=stdid)
    project = study.project
    if not check_view_permissions(request.user, project):
        return redirect('/unauthorized')

    assays = study.assay_of.all()
    factors = Factor.objects.filter(assay__study=study)
    signatures = Signature.objects.filter(factor__assay__study=study)
    return render(request, 'studies/details.html', {'project': project,'study': study, 'assays': assays, 'factors': factors, 'signatures': signatures})

# TODO : check for project edit permission
class EditStudyView(PermissionRequiredMixin, UpdateView):

    permission_required = 'change_project'

    model = Study
    template_name = 'studies/study_edit.html'
    form_class = StudyEditForm
    redirect_field_name="edit"
    login_url = "/unauthorized"
    context_object_name = 'edit'

    def get_permission_object(self):
        study = Study.objects.get(tsx_id=self.kwargs['stdid'])
        project = study.project
        return project

    def get_object(self, queryset=None):
        return Study.objects.get(tsx_id=self.kwargs['stdid'])

class CreateStudyView(PermissionRequiredMixin, CreateView):

    permission_required = 'change_project'
    login_url = "/unauthorized"
    redirect_field_name="create"
    model = Study
    template_name = 'studies/entity_create.html'
    form_class = StudyCreateForm

    def get_form_kwargs(self):
        kwargs = super(CreateStudyView, self).get_form_kwargs()
        if self.request.GET.get('clone'):
            studies = Study.objects.filter(tsx_id=self.request.GET.get('clone'))
            if studies.exists():
                study = studies.first()
                kwargs.update({'study': study})
        return kwargs

    def get_permission_object(self):
         project = Project.objects.get(tsx_id=self.kwargs['prjid'])
         return project

    # Autofill the user and project
    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.created_by = get_user(self.request)
        project = Project.objects.get(tsx_id=self.kwargs['prjid'])
        # Need safegards (access? exists?)
        self.object.project = project
        return super(CreateStudyView, self).form_valid(form)
