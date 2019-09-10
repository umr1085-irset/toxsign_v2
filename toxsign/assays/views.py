from django.contrib.auth import get_user_model, get_user
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.views import generic
from django.views.generic import CreateView, DetailView, ListView, RedirectView, UpdateView
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from guardian.mixins import PermissionRequiredMixin
from django.template.loader import render_to_string
from django.http import JsonResponse

from toxsign.projects.views import check_view_permissions, check_edit_permissions
from toxsign.projects.models import Project
from toxsign.assays.models import Assay, Factor
from toxsign.assays.forms import *
from toxsign.signatures.models import Signature

from django.db import transaction

def DetailAssayView(request, assid):

    assay = get_object_or_404(Assay, tsx_id=assid)
    project = assay.project
    if not check_view_permissions(request.user, project):
        return redirect('/index')

    factors = assay.factor_of.all()
    signatures = Signature.objects.filter(factor__assay=assay)
    return render(request, 'assays/assay_details.html', {'project': project, 'assay': assay, 'factors': factors,'signatures': signatures})

def DetailFactorView(request, facid):

    factor = get_object_or_404(Factor, tsx_id=facid)
    assay = factor.assay
    project = assay.project
    if not check_view_permissions(request.user, project):
        return redirect('/index')

    signatures = Signature.objects.filter(factor=factor)
    return render(request, 'assays/factor_details.html', {'project': project, 'assay': assay, 'factor': factor,'signatures': signatures})

class EditAssayView(PermissionRequiredMixin, UpdateView):
    permission_required = 'change_project'

    model = Assay
    template_name = 'assays/assay_edit.html'
    form_class = AssayEditForm
    redirect_field_name="edit"
    login_url = "/unauthorized"
    context_object_name = 'edit'

    def get_permission_object(self):
        self.assay = Assay.objects.get(tsx_id=self.kwargs['assid'])
        self.project = self.assay.project
        return self.project

    def get_object(self, queryset=None):
        #return Assay.objects.get(tsx_id=self.kwargs['assid'])
        return self.assay

    def get_form_kwargs(self):
        kwargs = super(EditAssayView, self).get_form_kwargs()
        projects = self.project
        kwargs.update({'project': projects})
        return kwargs

class EditFactorView(PermissionRequiredMixin, UpdateView):
    permission_required = 'change_project'

    model = Factor
    template_name = 'assays/factor_edit.html'
    form_class = FactorEditForm
    redirect_field_name="edit"
    login_url = "/unauthorized"
    context_object_name = 'edit'

    def get_permission_object(self):
        self.factor = Factor.objects.get(tsx_id=self.kwargs['facid'])
        self.project = self.factor.assay.project
        return self.project

    def get_object(self, queryset=None):
        #return Assay.objects.get(tsx_id=self.kwargs['assid'])
        return self.factor

    def get_form_kwargs(self):
        kwargs = super(EditFactorView, self).get_form_kwargs()
        assays = Assay.objects.filter(project=self.project).all()
        kwargs.update({'assay': assays})
        return kwargs

class CreateAssayView(PermissionRequiredMixin, CreateView):
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
        kwargs = super(CreateAssayView, self).get_form_kwargs()
        if self.request.GET.get('clone'):
            assays = Assay.objects.filter(tsx_id=self.request.GET.get('clone'))
            if assays.exists():
                assay = assays.first()
                kwargs.update({'assay ': assay})
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
        return super(CreateAssayView, self).form_valid(form)

class CreateFactorView(PermissionRequiredMixin, CreateView):
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
        kwargs = super(CreateFactorView, self).get_form_kwargs()

        if self.request.GET.get('selected'):
            assays = Assay.objects.filter(tsx_id=self.request.GET.get('selected'))
            if assays.exists():
                assay = assays.all()
                kwargs.update({'assay': assay})
            else:
                assays = Assay.objects.filter(project=self.project).all()
                kwargs.update({'assay': assays})
        else:
            assays = Assay.objects.filter(project=self.project).all()
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
        self.object.created_by = get_user(self.request)
        return super(CreateFactorView, self).form_valid(form)

class CreateChemicalsubFactorView(PermissionRequiredMixin, CreateView):
    model = ChemicalsubFactor
    template_name = 'assays/subfactor_edit.html'
    form_class = ChemicalsubFactorCreateForm
    redirect_field_name="create"
    permission_required = 'change_project'
    login_url = "/unauthorized"

    def get_permission_object(self):
        self.factor = get_object_or_404(Factor, tsx_id=self.kwargs['facid'])
        project = self.factor.assay.project
        return project

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        context['subfactor_name'] = "Chemical subfactor"
        return context

    # Autofill the user
    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.created_by = get_user(self.request)
        self.object.factor = self.factor
        return super(CreateChemicalsubFactorView, self).form_valid(form)

class EditChemicalsubFactorView(PermissionRequiredMixin, UpdateView):
    model = ChemicalsubFactor
    template_name = 'assays/subfactor_create.html'
    form_class = ChemicalsubFactorEditForm
    redirect_field_name="edit"
    permission_required = 'change_project'
    login_url = "/unauthorized"

    def get_permission_object(self):
        self.subfactor = get_object_or_404(ChemicalsubFactor, id=self.kwargs['id'])
        self.factor = self.subfactor.factor
        project = self.factor.assay.project
        return project

    def get_object(self, queryset=None):
        return self.subfactor

def get_subfactors(request, facid):

    factor = get_object_or_404(Factor, tsx_id=facid)
    project = factor.assay.project

    if not check_view_permissions(request.user, project):
        return redirect('/unauthorized')

    data = {}
    context = {'factor': factor, 'can_edit': check_edit_permissions(request.user, project)}

    data['html_form'] = render_to_string('assays/partial_subfactor_show.html',
        context,
        request=request,
    )

    return JsonResponse(data)

def delete_subfactor(request, type, id):

    if not request.user.is_authenticated:
        return redirect('/unauthorized')

    if type == "chemical":
        subfactor = get_object_or_404(ChemicalsubFactor, id=id)

    project = subfactor.factor.assay.project
    factor = subfactor.factor

    if not check_view_permissions(request.user, project):
        return redirect('/unauthorized')

    subfactor.delete()

    return redirect(reverse("assays:factor_detail", kwargs={"facid": factor.tsx_id}))
