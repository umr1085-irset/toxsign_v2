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
from toxsign.projects.models import Project
from toxsign.studies.models import Study
from toxsign.assays.models import Assay, Factor
from toxsign.assays.forms import AssayCreateForm, FactorCreateForm
from toxsign.signatures.models import Signature



def DetailView(request, assid):

    assay = get_object_or_404(Assay, tsx_id=assid)
    study = assay.study
    project = study.project
    if not check_view_permissions(request.user, project):
        return redirect('/index')

    factors = assay.factor_of.all()
    signatures = Signature.objects.filter(factor__assay=assay)
    return render(request, 'assays/details.html', {'project': project,'study': study, 'assay': assay, 'factors': factors,'signatures': signatures})


class AssayCreateView(PermissionRequiredMixin, CreateView):
    model = Assay
    template_name = 'assays/assay_create.html'
    form_class = AssayCreateForm
    redirect_field_name = "create"
    permission_required = 'change_project'
    login_url = "/unauthorized"

    def get_permission_object(self):
        self.project = get_object_or_404(Project, tsx_id=self.kwargs['prjid'])
        return self.project

    def get_form_kwargs(self):
        kwargs = super(AssayCreateView, self).get_form_kwargs()

        if self.request.GET.get('selected'):
            studies = Study.objects.filter(tsx_id=self.request.GET.get('selected'))
            if studies.exists():
                study = studies.all()
                kwargs.update({'study': study})
            else:
                studies = self.project.study_of.all()
                kwargs.update({'study': studies})
        else:
            studies = self.project.study_of.all()
            kwargs.update({'study': studies})

        if self.request.GET.get('clone'):
            assays = Assay.objects.filter(tsx_id=self.request.GET.get('clone'))
            if assays.exists():
                assay = assays.first()
                kwargs.update({'assay': assay})

        return kwargs

    # Autofill the user
    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.created_by = self.request.user
        return super(CreateView, self).form_valid(form)

class FactorCreateView(PermissionRequiredMixin, CreateView):
    model = Factor
    template_name = 'assays/factor_create.html'
    form_class = FactorCreateForm
    redirect_field_name="create"
    permission_required = 'change_project'
    login_url = "/unauthorized"

    def get_permission_object(self):
        self.project = Project.objects.get(tsx_id=self.kwargs['prjid'])
        return self.project

    def get_form_kwargs(self):
        kwargs = super(FactorCreateView, self).get_form_kwargs()

        if self.request.GET.get('selected'):
            assays = Assay.objects.filter(tsx_id=self.request.GET.get('selected'))
            if assays.exists():
                assay = assays.all()
                kwargs.update({'assay': assay})
            else:
                assays = Assay.objects.filter(study__project=self.project).all()
                kwargs.update({'assay': assays})
        else:
            assays = Assay.objects.filter(study__project=self.project).all()
            kwargs.update({'assay': assays})

        if self.request.GET.get('clone'):
            factors = Factor.objects.filter(tsx_id=self.request.GET.get('clone'))
            if factors.exists():
                factor = factors.first()
                kwargs.update({'factor': factor})

        return kwargs


    # Autofill the user
    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.created_by = self.request.user
        assay = Assay.objects.get(tsx_id=self.kwargs['assid'])
        # Need safegards (access? exists?)
        self.object.assay = assay
        return super(CreateView, self).form_valid(form)
