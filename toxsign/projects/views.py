from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.views import generic
from django.views.generic import DetailView, ListView, RedirectView, UpdateView
from django.shortcuts import redirect

from toxsign.projects.models import Project
from toxsign.projects.forms import ProjectForm
from toxsign.studies.models import Study
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def IndexView(request):
    Model_one = Project.objects.all().order_by('id')
    project_number = len(Model_one)
    paginator = Paginator(Model_one, 5)
    page = request.GET.get('projects')
    try:
        Model_one = paginator.page(page)
    except PageNotAnInteger:
        Model_one = paginator.page(1)
    except EmptyPage:
        Model_one = paginator.page(paginator.num_pages)

    Model_two = Study.objects.all()
    study_number = len(Model_two)
    paginator = Paginator(Model_two, 6)
    page = request.GET.get('studies')
    try:
        Model_two = paginator.page(page)
    except PageNotAnInteger:
        Model_two = paginator.page(1)
    except EmptyPage:
        Model_two = paginator.page(paginator.num_pages)

    context = {'project_list': Model_one, 'study_list': Model_two, 'project_number':project_number, 'study_number':study_number}
    return render(request, 'projects/index.html', context)

def DetailView(request, prjid):
    project_object = Project.objects.get(tsx_id=prjid)
    project = get_object_or_404(Project, pk=project_object.id)
    studies = project.study_of.all()
    print(studies)
    return render(request, 'projects/details.html', {'project': project,'st udies':studies})

class EditView(LoginRequiredMixin, UpdateView):

    model = Project
    template_name = 'projects/project_edit.html'
    fields = ["name", "description"]
    context_object_name = 'edit'

    def get_success_url(self):
        return reverse("project:details", kwargs={"prjid": edit.tsx_id})

    def get_object(self, queryset=None):
        return Project.objects.get(pk=self.kwargs['pk'])
