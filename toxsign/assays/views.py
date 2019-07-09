from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.views import generic
from django.views.generic import DetailView, ListView, RedirectView, UpdateView
from django.contrib.auth.decorators import login_required

from toxsign.assays.models import Assay


@login_required
def DetailView(request, assid):

    assay = get_object_or_404(Assay, tsx_id=assid)
    study = assay.study
    project = study.project
    factors = assay.factor_of
    signatures = Signature.objects.filter(factor__assay=factor)
    return render(request, 'assays/details.html', {'project': project,'study': study, 'assay': assay, 'factors': factors,'signatures': signatures})
