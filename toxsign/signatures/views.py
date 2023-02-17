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

from toxsign.projects.views import check_view_permissions
from toxsign.projects.models import Project
from toxsign.assays.models import Assay, Factor
from toxsign.signatures.models import Signature
from toxsign.signatures.forms import SignatureCreateForm, SignatureEditForm

from toxsign.projects.documents import ProjectDocument
from toxsign.signatures.documents import SignatureDocument
from elasticsearch_dsl import Q as Q_es

from dal import autocomplete
from django.db.models import Q

class SignatureToolAutocomplete(autocomplete.Select2QuerySetView):

    def get_queryset(self):
        try:
            excluded_projects =  ProjectDocument.search().sort('id').query(Q_es(Q_es("match", status="PRIVATE") | Q_es("match", status="PENDING"))).scan()
            # Limit all query to theses projects
            excluded_projects_id_list = [project.id for project in excluded_projects if not check_view_permissions(self.request.user, project)]

            docs = Q_es("match", down_gene_number=0) & Q_es("match", up_gene_number=0)
            qs = SignatureDocument.search().sort('id').exclude("terms", factor__assay__project__id=excluded_projects_id_list).exclude(docs)
            query = self.q
            if query:
                query = "*" + query + "*"
                query = query.replace("-", " ")
                q1 = Q_es('bool', must=[Q_es("query_string", query=quer) for quer in query.split(" ")])
                res = qs.filter(q1)

            return res
        # Fall back to DB search if failure for any reason
        except Exception as e:
            qs = Signature.objects.all()
            if query:
                qs = qs.filter(Q(tsx_id__istartswith=query))
        return qs

    def get_result_value(self, result):
        return result.id

    def get_result_label(self, result):
        return result.tsx_id + " - " + result.name

def DetailView(request, sigid):

    signature = get_object_or_404(Signature, tsx_id=sigid)
    factor = signature.factor
    chem_subfactors = factor.chemical_subfactor_of.all()
    assay = factor.assay
    project = assay.project

    if not check_view_permissions(request.user, project):
        return redirect('/unauthorized')

    return render(request, 'signatures/details.html', {'project': project, 'assay': assay, 'factor': factor, 'chem_subfactors': chem_subfactors, 'signature': signature})

class EditSignatureView(PermissionRequiredMixin, UpdateView):
    permission_required = 'change_project'

    model = Signature
    template_name = 'signatures/signature_edit.html'
    form_class = SignatureEditForm
    redirect_field_name="edit"
    login_url = "/unauthorized"
    context_object_name = 'edit'

    def get_permission_object(self):
        self.signature = Signature.objects.get(tsx_id=self.kwargs['sigid'])
        self.project = self.signature.factor.assay.project
        if self.project.status == "PUBLIC":
            return redirect(reverse("projects:detail", kwargs={"prjid": self.project.tsx_id}))
        return self.project

    def get_object(self, queryset=None):
        return self.signature

    def get_form_kwargs(self):
        kwargs = super(EditSignatureView, self).get_form_kwargs()
        factors = Factor.objects.filter(assay__project = self.project)
        kwargs.update({'factor': factors})
        return kwargs

class CreateSignatureView(PermissionRequiredMixin, CreateView):

    permission_required = 'change_project'
    login_url = "/unauthorized"
    redirect_field_name = "create"
    model = Signature
    form_class = SignatureCreateForm
    template_name = 'signatures/entity_create.html'

    def get_permission_object(self):
        self.project = Project.objects.get(tsx_id=self.kwargs['prjid'])
        if self.project.status == "PUBLIC":
            return redirect(reverse("projects:detail", kwargs={"prjid": self.project.tsx_id}))
        return self.project

    def get_form_kwargs(self):

        kwargs = super(CreateSignatureView, self).get_form_kwargs()

        if self.request.GET.get('selected'):
            factors = Factor.objects.filter(tsx_id=self.request.GET.get('selected'))
            if factors.exists():
                factor = factors.all()
                kwargs.update({'factor': factor})
            else:
                factors = Factor.objects.filter(assay__project = self.project)
                kwargs.update({'factor': factors})
        else:
            factors = Factor.objects.filter(assay__project = self.project)
            kwargs.update({'factor': factors})


        if self.request.GET.get('clone'):
            sigs = Signature.objects.filter(tsx_id=self.request.GET.get('clone'))
            if sigs.exists():
                sig = sigs.first()
                kwargs.update({'sig': sig})

        return kwargs

    # Autofill the user
    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.created_by = get_user(self.request)
        return super(CreateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('jobs:running_jobs')
