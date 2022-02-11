from django.urls import path
from toxsign.superprojects import views

app_name = "superprojects"
urlpatterns = [
    path('create/', views. create_superproject, name='superproject_create'),
    path('edit/<str:spjid>/', views.edit_superproject, name='superproject_edit'),
    path('unlink/<str:spjid>/<str:prjid>', views.unlink_project, name='superproject_unlink'),
    path('<str:spjid>/', views.DetailView, name='detail')
]
