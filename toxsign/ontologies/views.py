from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.views import generic
from django.views.generic import DetailView, ListView, RedirectView, UpdateView
from toxsign.ontologies.models import Biological

class IndexView(generic.ListView):
    model = Biological
    template_name = 'ontologies/index.html'
    context_object_name = 'onto_list'


class DetailView(LoginRequiredMixin, DetailView):
    model = Biological
    template_name = 'ontologies/detail.html'
    context_object_name = 'onto_list'
