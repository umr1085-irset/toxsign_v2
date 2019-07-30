from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.views import generic
from django.views.generic import CreateView, DetailView, ListView, RedirectView, UpdateView
from django.contrib.auth.decorators import login_required

from guardian.mixins import PermissionRequiredMixin

from toxsign.projects.views import check_view_permissions
from toxsign.assays.models import Assay
from toxsign.signatures.models import Signature
from toxsign.signatures.forms import SignatureCreateForm


def DetailView(request, sigid):

    signature = get_object_or_404(Signature, tsx_id=sigid)
    assay = signature.factor.assay
    study = assay.study
    project = study.project

    if not check_view_permissions(request.user, project):
        return redirect('/unauthorized')

    return render(request, 'signatures/details.html', {'project': project,'study': study, 'assay': assay, 'signature': signature})

class CreateView(PermissionRequiredMixin, CreateView):

    permission_required = 'change_project'
    login_url = "/unauthorized"
    redirect_field_name = "create"
    model = Signature
    form_class = SignatureCreateForm
    template_name = 'signatures/entity_create.html'

    def get_permission_object(self):
        assay = Assay.objects.get(tsx_id=self.kwargs['assid'])
        project = assay.study.project
        return project

    # We need to get the assay id to restrict the factors (since we don't pass a factor id to the form directly)
    def get_form_kwargs(self):
        kwargs = super(CreateView, self).get_form_kwargs()
        kwargs.update({'assid': self.kwargs.get('assid')})
        return kwargs

    # Autofill the user
    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.created_by = self.request.user
        return super(CreateView, self).form_valid(form)
