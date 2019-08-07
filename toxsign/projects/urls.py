from django.urls import path
from toxsign.projects import views

app_name = "projects"
urlpatterns = [
    path('create/', views.CreateProjectView.as_view(), name='project_create'),
    path('<str:prjid>/', views.DetailView, name='detail'),
    path('edit/<str:prjid>/', views.EditProjectView.as_view(), name='project_edit')
]
