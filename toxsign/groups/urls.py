from django.urls import path
from toxsign.groups import views

app_name = "groups"
urlpatterns = [
    path('<int:grpid>/', views.DetailView, name='detail'),
    path('<int:group_id>/remove/<int:user_to_remove_id>', views.remove_user_from_group, name='remove_user'),
]
