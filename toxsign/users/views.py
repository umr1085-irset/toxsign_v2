from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import DetailView, ListView, RedirectView, UpdateView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.template.loader import render_to_string
from django.http import JsonResponse
from django.shortcuts import redirect

from toxsign.superprojects.models import Superproject
from toxsign.projects.models import Project
from toxsign.projects.views import get_access_type, check_view_permissions
from toxsign.users.models import Notification
from config.views import paginate


User = get_user_model()


class UserDetailView(LoginRequiredMixin, DetailView):

    model = User
    slug_field = "username"
    slug_url_kwarg = "username"

    def get_context_data(self, **kwargs):
        context = super(UserDetailView, self).get_context_data(**kwargs)
        groups = self.request.user.groups.all()
        superprojects = Superproject.objects.filter(created_by=self.request.user)

        try:

            if request.user.is_superuser:
                q = Q_es()
            else:
                groups = [group.id for group in request.user.groups.all()]
                q = Q_es("match", created_by__username=request.user.username)  | Q_es('nested', path="read_groups", query=Q_es("terms", read_groups__id=groups))

            projects =  paginate(ProjectDocument.search().query(q), self.request.GET.get('projects'), 5, True)

        except:
            projects = paginate([project for project in Project.objects.all() if check_view_permissions(self.request.user, project, True)], self.request.GET.get('projects'), 5)

        context['groups'] = paginate(groups, self.request.GET.get('groups'), 5)
        context['superprojects'] = paginate(superprojects, self.request.GET.get('superprojects'), 5)
        context['notifications'] = paginate(Notification.objects.filter(user=self.request.user), self.request.GET.get('notifications'), 5)
        context['projects'] = projects

        for group in context['groups']:
            group.members_number = group.user_set.count()
        for project in context['projects']:
            project.permissions = get_access_type(self.request.user, project)

        context['in_use'] = {
            'user': "",
            'superproject': "",
            'project': "",
            'notification': ""
        }

        if self.request.GET.get('projects'):
            context['in_use']['project'] = 'active'
        elif self.request.GET.get('notification'):
            context['in_use']['notification'] = 'active'
        elif self.request.GET.get('superproject'):
            context['in_use']['superproject'] = 'active'
        else:
            context['in_use']['user'] = 'active'

        return context

user_detail_view = UserDetailView.as_view()


class UserListView(LoginRequiredMixin, ListView):

    model = User
    slug_field = "username"
    slug_url_kwarg = "username"


user_list_view = UserListView.as_view()


class UserUpdateView(LoginRequiredMixin, UpdateView):

    model = User
    fields = ["name", "last_name", "institut"]

    def get_success_url(self):
        return reverse("users:detail", kwargs={"username": self.request.user.username})

    def get_object(self):
        return User.objects.get(username=self.request.user.username)


user_update_view = UserUpdateView.as_view()

class UserRedirectView(LoginRequiredMixin, RedirectView):

    permanent = False

    def get_redirect_url(self):
        return reverse("users:detail", kwargs={"username": self.request.user.username})


user_redirect_view = UserRedirectView.as_view()


def dismiss_notification(request, notification_id):
    notification = Notification.objects.get(id=notification_id)

    if not request.user == notification.user:
        return redirect('/unauthorized')

    data = dict()
    if request.method == 'POST':
        notification.delete()
        data = {'form_is_valid': True, 'redirect': reverse("users:detail", kwargs={"username": request.user.username}) + "?notification=true"}
    else:
       context = {'group': notification.group, 'notification': notification}
       data['html_form'] = render_to_string('users/partial_notif_dismiss.html',
           context,
           request=request,
       )
    return JsonResponse(data)


def accept_group_invitation(request, notification_id):
    notification = Notification.objects.get(id=notification_id)

    # Check group is set
    if not notification.group:
        # Need a better redirection, though this should not happen
        notification.delete()
        return redirect('/unauthorized')

    if not request.user == notification.user:
        return redirect('/unauthorized')

    if not request.user in notification.group.user_set.all():
        notification.group.user_set.add(request.user)

    notification.delete()
    data = {'form_is_valid': True, 'redirect': reverse("users:detail", kwargs={"username": request.user.username}) + "?notification=true"}
    return JsonResponse(data)

def is_viewable(entity, user):
    can_view = False

    if user.is_authenticated:
        if entity.created_by == user:
            can_view = True
    else:
        if entity.created_by == None:
            can_view = True

    return can_view
