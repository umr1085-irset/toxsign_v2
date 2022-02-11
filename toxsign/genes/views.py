import os
import json
from datetime import datetime

from dal import autocomplete
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
from django.template.loader import render_to_string
from django.db.models import Q

from django.views.generic import CreateView

import uuid
import shutil
from .models import Gene

class GeneAutocomplete(autocomplete.Select2QuerySetView):

    def get_result_value(self, result):
        return result.id

    def get_result_label(self, result):
        return result.symbol

    def get_queryset(self):
        query = self.q
        qs = Gene.objects.all()
        if query:
            qs = qs.filter(Q(symbol__icontains=query) | Q(synonyms__icontains=query)| Q(gene_id__icontains=query))
        return qs

def get_gene(request, gene_id):

    gene = get_object_or_404(Gene, id=gene_id)
    data = {'gene_id' : gene.gene_id, "symbol": gene.symbol, "homolog_id": gene.homolog_id, "ensembl_id": gene.ensemble_id}
    return JsonResponse(data)
