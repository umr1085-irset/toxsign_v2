from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.views import generic
from django.views.generic import CreateView, DetailView, ListView, RedirectView, UpdateView
from django.contrib.auth.decorators import login_required

from toxsign.assays.models import Assay
from toxsign.signatures.models import Signature
from toxsign.signatures.forms import SignatureCreateForm


@login_required
def DetailView(request, sigid):

    signature = get_object_or_404(Signature, tsx_id=sigid)
    assay = signature.factor.assay
    study = assay.study
    project = study.project
    return render(request, 'signatures/details.html', {'project': project,'study': study, 'assay': assay, 'signature': signature})

class CreateView(LoginRequiredMixin, CreateView):
    model = Signature
    template_name = 'pages/entity_create.html'
    assay = Assay.objects.get(tsx_id=self.kwargs['assid'])
    # Need safegards (access? exists?)
    form_class = SignatureCreateForm(assay)

    # Autofill the user
    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.created_by = self.request.user
        return super(CreateView, self).form_valid(form)
