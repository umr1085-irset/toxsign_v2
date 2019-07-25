from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import DetailView, ListView, RedirectView, UpdateView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


from toxsign.projects.models import Project
from toxsign.projects.views import get_access_type, check_view_permissions
from toxsign.users.models import Notification

User = get_user_model()


class UserDetailView(LoginRequiredMixin, DetailView):

    model = User
    slug_field = "username"
    slug_url_kwarg = "username"

    def get_context_data(self, **kwargs):
        context = super(UserDetailView, self).get_context_data(**kwargs)
        groups = self.request.user.groups.all()
        projects = Project.objects.all().order_by('id')
        context['permissions'] = {}
        context['groups'] = groups
        notifications = Notification.objects.filter(user=self.request.user)
        context['notifications'] = notifications
        context['notification_number'] = notifications.count()
        for group in context['groups']:
            group.members_number = group.user_set.count()
        context['group_number'] = len(groups)
        context['project_list'] = [project for project in projects if check_view_permissions(self.request.user, project)]
        context['in_use'] = {
            'user': "",
            'project': "",
        }
        if self.request.GET.get('projects'):
            context['in_use']['project'] = 'active'
        else:
            context['in_use']['user'] = 'active'

        for project in context['project_list']:
            project.permissions = get_access_type(self.request.user, project)

        context['project_number'] = len(context['project_list'])
        paginator = Paginator(context['project_list'], 5)
        page = self.request.GET.get('projects')
        try:
            context['project_list'] = paginator.page(page)
        except PageNotAnInteger:
            context['project_list'] = paginator.page(1)
        except EmptyPage:
            context['project_list'] = paginator.page(paginator.num_pages)

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
        redirect('/unauthorized')

    notification.delete()
    data = {'form_is_valid': True}
    return JsonResponse(data)


def accept_group_invitation(request, notification_id):
    notification = Notification.objects.get(id=notification_id)

    # Check group is set
    if not notification.group:
        # Need a better redirection, though this should not happen
        notification.delete()
        redirect('/unauthorized')

    if not request.user == notification.user:
        redirect('/unauthorized')

    if not request.user in notification.group.user_set.all():
        notification.group.user_set.add(request.user)

    notification.delete()
    data = {'form_is_valid': True}
    return JsonResponse(data)
