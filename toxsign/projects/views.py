from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.views import generic
from django.views.generic import DetailView, ListView, RedirectView, UpdateView
from django.shortcuts import redirect

from toxsign.assays.models import Assay
from toxsign.projects.models import Project
from toxsign.signatures.models import Signature
from toxsign.studies.models import Study



def DetailView(request, prjid):
    project_object = Project.objects.get(tsx_id=prjid)
    project = get_object_or_404(Project, pk=project_object.id)
    studies = project.study_of.all()
    assays = Assay.objects.filter(study__project=project)
    signatures = Signature.objects.filter(factor__assay__study__project=project)
    return render(request, 'projects/details.html', {'project': project,'studies': studies, 'assays': assays, 'signatures': signatures})

class EditView(LoginRequiredMixin, UpdateView):

    model = Project
    template_name = 'projects/project_edit.html'
    fields = ["name", "description"]
    context_object_name = 'edit'

    def get_object(self, queryset=None):
        return Project.objects.get(pk=self.kwargs['pk'])
