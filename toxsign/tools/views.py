import os
from datetime import datetime

from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.views import View
from django.shortcuts import redirect
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.contrib import messages

import uuid
import shutil

from toxsign.tools.models import Tool
from toxsign.tools.forms import python_printForm
from toxsign.jobs.models import Job

# Create your views here.
class IndexView(LoginRequiredMixin, generic.ListView):
    template_name = 'tools/index.html'
    context_object_name = 'tools_list'

    def get_queryset(self):
        """
        Return the last five published questions (not including those set to be
        published in the future).
        """
        return Tool.objects.filter(
            created_at__lte=timezone.now()
        ).order_by('-created_at')[:5]

class DetailView(LoginRequiredMixin, generic.DetailView):
    model = Tool
    template_name = 'tools/detail.html'
    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Tool.objects.filter(created_at__lte=timezone.now())