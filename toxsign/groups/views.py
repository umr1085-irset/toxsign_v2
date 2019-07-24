from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.shortcuts import redirect
from guardian.shortcuts import get_perms
from django.contrib.auth.models import Group
from toxsign.users.models import User
from django.template.loader import render_to_string
from django.http import JsonResponse

# TODO : clear 403 page redirect (page with an explanation?)
def DetailView(request, grpid):
    group = request.user.groups.filter(id=grpid)

    if not group.count():
        return redirect('/unauthorized')

    data = {
        'group': group.get(),
        'users' : group.get().user_set.all()
    }
    return render(request, 'groups/group_detail.html', data)

def remove_user_from_group(request, group_id, user_to_remove_id):
    group = get_object_or_404(Group, pk=group_id)
    # Check user is owner
    # And target is not owner
    if not request.user == group.ownership.owner:
        redirect('/unauthorized')

    user = get_object_or_404(User, pk=user_to_remove_id)

    if group.ownership.owner == user:
    # TODO: Give a proper error instead
        redirect('/unauthorized')

    data = dict()
    if request.method == 'POST':
        group.user_set.remove(user)
        data['form_is_valid'] = True
    else:
        context = {'group': group, 'user': user}
        data['html_form'] = render_to_string('groups/partial_user_remove.html',
            context,
            request=request,
        )
    return JsonResponse(data)
