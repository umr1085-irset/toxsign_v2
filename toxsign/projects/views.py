from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.views import generic
from django.views.generic import DetailView, ListView, RedirectView, UpdateView
from toxsign.projects.models import Project
from toxsign.studies.models import Study

User = get_user_model()

class IndexView(generic.ListView):
    template_name = 'projects/index.html'
    context_object_name = 'project_list'

    def get_queryset(self):
        """
        Return the last five published questions (not including those set to be
        published in the future).
        """
        return Project.objects.filter(
            created_at__lte=timezone.now()
        ).order_by('created_at')

def DetailView(request, prjid):
    project_object = Project.objects.get(prj_id=prjid)
    project = get_object_or_404(Project, pk=project_object.id)
    studies = project.study_of.all()
    print(studies)
    return render(request, 'projects/details.html', {'project': project,'studies':studies})