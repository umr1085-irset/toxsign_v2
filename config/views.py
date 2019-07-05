from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.views import generic
from django.views.generic import DetailView, ListView, RedirectView, UpdateView
from django.http import HttpResponse
from django.db.models import Q

import json

from toxsign.projects.models import Project
from toxsign.studies.models import Study
from toxsign.signatures.models import Signature

def HomeView(request):
        context = {}
        return render(request, 'pages/home.html',context)

def autocompleteModel(request):
    query = request.GET.get('q')
    results_projects = Project.objects.filter(Q(name__icontains=query) | Q(description__icontains=query) | Q(tsx_id__icontains=query))
    results_studies = Study.objects.filter(Q(name__icontains=query) | Q(description__icontains=query) | Q(tsx_id__icontains=query))
    results_signatures = Signature.objects.filter(Q(name__icontains=query) | Q(tsx_id__icontains=query))
    results = {
        'projects_number' : len(results_projects),
        'studies_number' : len(results_studies),
        'signatures_number' : len(results_signatures),
        'projects': results_projects,
        'studies': results_studies,
        'signatures': results_signatures
    }
    return render(request, 'pages/ajax_search.html', {'statuss': results})

def search(request,query):
    print(query)
    search_qs = Project.objects.filter(name__contains=query)
