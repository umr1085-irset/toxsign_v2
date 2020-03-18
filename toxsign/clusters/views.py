from django.contrib.auth import get_user_model, get_user
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.views.generic import DetailView, ListView, RedirectView, UpdateView, CreateView
from django.shortcuts import redirect
from guardian.mixins import PermissionRequiredMixin
from guardian.shortcuts import get_perms

from django.template.loader import render_to_string
from django.http import JsonResponse
from toxsign.clusters.models import Cluster

import pandas as pd
import numpy as np
from django.core.mail import mail_admins

def index(request):

    # Todo : autosetup based on method
    euclidean_clusters = Cluster.objects.filter(distance_method="euclidean")
    correlation_cluster = Cluster.objects.filter(distance_method="correlation")

    return render(request, 'clusters/index.html',{"euclidean": euclidean_clusters, "correlation": correlation_cluster})

def details(request, type, clrid):

    if not type in ['correlation', 'euclidean']:
        return redirect(reverse("home"))

    cluster = get_object_or_404(Cluster, distance_method=type, cluster_id=clrid)
    return render(request, 'clusters/details.html',{"cluster": cluster})


def get_graph_data(request, type, clrid):

    data = {"data": [{"x": [], "y": [], "type": "bar", "text": []}]}

    if not type in ['correlation', 'euclidean']:
        return JsonResponse()

    enrich_type = request.GET.get("type")
    if not enrich_type or not (enrich_type == "chem" or enrich_type == "gene"):
        type= "chem"

    cluster = get_object_or_404(Cluster, distance_method=type, cluster_id=clrid)

    if enrich_type == "chem" and cluster.chemical_enrichment_file:
        data = _format_graph_data(cluster.chemical_enrichment_file.path, "Chemical enrichment")

    elif enrich_type == "gene" and cluster.gene_enrichment_file:
        data = _format_graph_data(cluster.gene_enrichment_file.path, "Gene enrichment")

    return JsonResponse(data)

def _format_graph_data(file_path, title, rows=10):

    df = pd.read_csv(file_path, sep="\t", encoding="latin1")
    df = df[['MESH', 'pBH', 'r']]
    df = df[df.pBH != 1]
    df = df.sort_values(['pBH', 'r'], ascending=(True,False))
    df = df.head(rows)
    df['pBH'] = -np.log(df['pBH'])
    df['MESH'] = df['MESH'].apply(_clean_name)
    df['r'] = df['r'].apply(lambda x: "r = " + str(x))

    layout = {
        "title": title,
        "yaxis": {
            "automargin": True,
            "autorange":"reversed"
        },
        "xaxis": {
            "title": {"text": "-log(Adjusted P value)"},
        },
    };

    return {
        "data": [{
            "x": df['pBH'].values.tolist(),
            "y": df['MESH'].values.tolist(),
            "type": "bar",
            "orientation": "h",
            "text": df['r'].values.tolist(),
            "textposition": 'auto',
            "hoverinfo": 'none',
        }],
        "layout": layout

    }

def _clean_name(string):

    string = string.replace("..MESH", " (MESH")
    string = string[:-1] + ") "
    string = string.replace("..", " ")
    string = string.replace(".", " ")
    return string

