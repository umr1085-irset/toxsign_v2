from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.views import generic
from django.views.generic import DetailView, ListView, RedirectView, UpdateView
from toxsign.studies.models import Study

User = get_user_model()

class IndexView(generic.ListView):
    template_name = 'studies/index.html'
    context_object_name = 'study_list'

    def get_queryset(self):
        """
        Return the last five published questions (not including those set to be
        published in the future).
        """
        return Studies.objects.filter(
            created_at__lte=timezone.now()
        ).order_by('created_at')

def DetailView(request, stdid):
    study_object = Studies.objects.get(std_id=stdid)
    study = get_object_or_404(Studies, pk=study_object.id)
    return render(request, 'studies/details.html', {'study': study})