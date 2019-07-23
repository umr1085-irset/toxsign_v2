from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import DetailView, ListView, RedirectView, UpdateView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


from toxsign.projects.models import Project

User = get_user_model()


class UserDetailView(LoginRequiredMixin, DetailView):

    model = User
    slug_field = "username"
    slug_url_kwarg = "username"
    def get_context_data(self, **kwargs):
        context = super(UserDetailView, self).get_context_data(**kwargs)
        groups = self.request.user.groups.all()
        context['groups'] = groups
        context['group_number'] = len(groups)
        context['project_list'] = Project.objects.filter(created_by__exact=self.request.user.id).order_by('id')
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
