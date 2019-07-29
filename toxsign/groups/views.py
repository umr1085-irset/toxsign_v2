from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.shortcuts import redirect
from guardian.shortcuts import get_perms
from django.views.generic import CreateView
from django.contrib.auth.models import Group

from django.db.models import Q
from toxsign.groups.forms import GroupCreateForm, GroupInvitationForm
from toxsign.users.models import User, Notification
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect


# TODO : clear 403 page redirect (page with an explanation?)
def DetailView(request, grpid):
    group = request.user.groups.filter(id=grpid)

    if not group.count():
        return redirect('/unauthorized')

    data = {
        'group': group.get(),
        'users': group.get().user_set.all(),
        'notifications': group.get().add_notifications.all()
    }
    return render(request, 'groups/group_detail.html', data)

class GroupCreateView(LoginRequiredMixin, CreateView):
    model = Group
    template_name = 'groups/entity_create.html'
    form_class = GroupCreateForm

     # Autofill the owner
    def form_valid(self, form):
        self.object = form.save()
        # Add owner here + add owner to members
        self.object.ownership.owner = self.request.user
        self.object.ownership.save()
        self.object.user_set.add(self.request.user)
        return HttpResponseRedirect(reverse("groups:detail", kwargs={"grpid": self.object.id}))

def send_invitation(request, group_id):
    group = get_object_or_404(Group, pk=group_id)

    if not request.user == group.ownership.owner:
         redirect('/unauthorized')

    data = {}
    if request.method == 'POST':
        form = GroupInvitationForm(request.POST)
        if form.is_valid():
            object = form.save(commit=False)
            object.created_by = request.user
            object.group = group
            object.type = "GROUP"
            object.message = "Invitation to the group " + group.name
            object.save()
            data['redirect'] = reverse("groups:detail", kwargs={"grpid": group_id})
            data['form_is_valid'] = True
    else:
        users = User.objects.exclude(Q(groups=group) | Q(notifications__group=group) | Q(username="AnonymousUser")).all()
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
         redirect('/unauthorized')

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
        redirect('/unauthorized')

    if group.ownership.owner == user:
    # TODO: Give a proper error instead
        redirect('/unauthorized')

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
