from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.shortcuts import redirect
from guardian.shortcuts import get_perms, get_objects_for_group
from django.views.generic import CreateView
from django.contrib.auth.models import Group

from django.db.models import Q
from toxsign.groups.forms import GroupCreateForm, GroupInvitationForm
from toxsign.users.models import User, Notification
from toxsign.projects.models import Project
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect


# TODO : clear 403 page redirect (page with an explanation?)
def DetailView(request, grpid):
    group = request.user.groups.filter(id=grpid).get()

    if not group:
        return redirect('/unauthorized')

    data = {
        'group': group,
        'users': group.user_set.all(),
        'notifications': group.add_notifications.all(),
        'read_access': get_objects_for_group(group, 'view_project', Project),
        'edit_access': get_objects_for_group(group, 'change_project', Project)
    }
    return render(request, 'groups/group_detail.html', data)

def create_group(request):

    if not request.user.is_authenticated:
        return redirect('/unauthorized')

    data = {}
    if request.method == 'POST':
        form = GroupCreateForm(request.POST)
        if form.is_valid():
            object = form.save()
            object.ownership.owner = request.user
            object.ownership.save()
            object.user_set.add(request.user)
            data['redirect'] = reverse("groups:detail", kwargs={"grpid": object.id})
            data['form_is_valid'] = True
        else:
            data['form_is_valid'] = False
    else:
        form = GroupCreateForm()

    context = {'form': form}
    data['html_form'] = render_to_string('groups/partial_group_create.html',
        context,
        request=request,
    )

    return JsonResponse(data)

def send_invitation(request, group_id):
    group = get_object_or_404(Group, pk=group_id)
    users = User.objects.exclude(Q(groups=group) | Q(notifications__group=group) | Q(username="AnonymousUser")).all()

    if not request.user == group.ownership.owner:
         return redirect('/unauthorized')

    data = {}
    if request.method == 'POST':
        form = GroupInvitationForm(request.POST)

        if not form.is_valid():
            data['form_is_valid'] = False

        elif not users.filter(id=request.POST['user']).exists():
            form = GroupInvitationForm(users=users)
            data['form_is_valid'] = False
            data['error'] = "This user is either already in the group, or has already an invitation pending. Please select another."

        else:
            object = form.save(commit=False)
            object.created_by = request.user
            object.group = group
            object.type = "GROUP"
            object.message = "Invitation to the group " + group.name
            object.save()
            data['redirect'] = reverse("groups:detail", kwargs={"grpid": group_id})
            data['form_is_valid'] = True
    else:
        form = GroupInvitationForm(users=users)

    context = {'form': form, 'group': group}
    data['html_form'] = render_to_string('groups/partial_user_add.html',
        context,
        request=request,
    )

    return JsonResponse(data)

def set_owner(request, group_id, new_owner_id):
    group = get_object_or_404(Group, pk=group_id)
    # Check user is owner
    # And target is not owner
    if not request.user == group.ownership.owner:
         return redirect('/unauthorized')

    user = get_object_or_404(User, pk=new_owner_id)
    data = {}

    if request.method == 'POST':
        if not group.ownership.owner == user:
            group.ownership.owner = user
            group.ownership.save()

        data['redirect'] = reverse("groups:detail", kwargs={"grpid": group_id})
        data['form_is_valid'] = True
    else:
        context = {'group': group, 'user': user}
        data['html_form'] = render_to_string('groups/partial_owner_change.html',
            context,
            request=request,
         )
    return JsonResponse(data)

def remove_user_from_group(request, group_id, user_to_remove_id):
    group = get_object_or_404(Group, pk=group_id)
    # Check user is owner
    # And target is not owner

    user = get_object_or_404(User, pk=user_to_remove_id)

    if not request.user == group.ownership.owner and not request.user == user:
        return redirect('/unauthorized')

    if group.ownership.owner == user:
    # TODO: Give a proper error instead
        return redirect('/unauthorized')

    data = dict()
    if request.method == 'POST':
        group.user_set.remove(user)
        data['form_is_valid'] = True
        if request.user == user:
            data['redirect'] = reverse("users:detail", kwargs={"username": request.user.username})
        else:
            data['redirect'] = reverse("groups:detail", kwargs={"grpid": group.id})
    else:
        context = {'group': group, 'user': user, 'self': request.user == user}
        data['html_form'] = render_to_string('groups/partial_user_remove.html',
            context,
            request=request,
        )
    return JsonResponse(data)
