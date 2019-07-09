from django.urls import path
from toxsign.projects import views

app_name = "projects"
urlpatterns = [
    path('<str:prjid>/', views.DetailView, name='detail'),
    path('project_edit/<int:pk>/', views.EditView.as_view(), name='project_edit'),
]
