from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.views import generic
from django.views.generic import DetailView, ListView, RedirectView, UpdateView
from toxsign.signatures.models import Signature


class IndexView(generic.ListView):
    template_name = 'signature/index.html'
    context_object_name = 'signatures'

    def get_queryset(self):
        """
        Return the last five published questions (not including those set to be
        published in the future).
        """
        return Signature.objects.filter(
            created_at__lte=timezone.now()
        ).order_by('created_at')

class DetailView(LoginRequiredMixin, DetailView):
    template_name = 'signature/details.html'
    model = Signature
    context_object_name = 'signature'

    def get_object(self, queryset=None):
            return Signature.objects.get(tsx_id=self.kwargs['sigid'])
