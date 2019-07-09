from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.views import generic
from django.views.generic import DetailView, ListView, RedirectView, UpdateView
from django.contrib.auth.decorators import login_required

from toxsign.signatures.models import Signature


@login_required
def DetailView(request, sigid):

    signature = get_object_or_404(Signature, tsx_id=sigid)
    assay = signature.factor.assay
    study = assay.study
    project = study.project
    return render(request, 'assays/details.html', {'project': project,'study': study, 'assay': assay, 'signature': signature})
