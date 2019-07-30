from django.urls import path
from toxsign.groups import views

app_name = "groups"
urlpatterns = [
    path('<int:grpid>/', views.DetailView, name='detail'),
    path('create/', views.create_group, name='create'),
    path('invite/<int:group_id>', views.send_invitation, name='invite_user'),
    path('<int:group_id>/remove/<int:user_to_remove_id>', views.remove_user_from_group, name='remove_user'),
    path('<int:group_id>/changeowner/<int:new_owner_id>', views.set_owner, name='change_owner'),
]
