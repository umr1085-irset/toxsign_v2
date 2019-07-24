from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.views.generic import DetailView, ListView, RedirectView, UpdateView, CreateView
from django.shortcuts import redirect
from guardian.mixins import PermissionRequiredMixin
from guardian.shortcuts import get_perms


# TODO : clear 403 page redirect (page with an explanation?)
def DetailView(request, grpid):
    group = user.groups.filter(id=grpid)

    if not group.exist()
        return redirect('/unauthorized')

    data = {
        'group': group,
        'users' : group.user_set.all(),
    }
    return render(request, 'groups/group_detail.html', data)
