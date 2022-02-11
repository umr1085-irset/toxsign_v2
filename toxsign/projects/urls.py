from django.urls import path
from toxsign.projects import views

app_name = "projects"
urlpatterns = [
    path('create/', views.CreateProjectView.as_view(), name='project_create'),
    path('edit/<str:prjid>/', views.EditProjectView.as_view(), name='project_edit'),
    path('publicize/<str:prjid>/', views.publicize_project, name='project_publicize'),
    path('<str:prjid>/', views.DetailView, name='detail'),
]
