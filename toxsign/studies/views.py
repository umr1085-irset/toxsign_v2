from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.views import generic
from django.views.generic import DetailView, ListView, RedirectView, UpdateView
from django.contrib.auth.decorators import login_required

from toxsign.assays.models import Assay
from toxsign.projects.models import Project
from toxsign.signatures.models import Signature
from toxsign.studies.models import Study


@login_required
def DetailView(request, stdid):

    study = get_object_or_404(Study, tsx_id=stdid)
    project = study.project
    assays = Assay.objects.filter(study=study)
    signatures = Signature.objects.filter(factor__assay__study=study)
    return render(request, 'studies/details.html', {'project': project,'study': study, 'assays': assays, 'signatures': signatures})


class EditView(LoginRequiredMixin, UpdateView):

    model = Study
    template_name = 'studies/study_edit.html'
    fields = ["name", "description"]
    context_object_name = 'edit'

    def get_object(self, queryset=None):
        return Study.objects.get(pk=self.kwargs['pk'])
