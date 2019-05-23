from django.urls import path
from toxsign.projects import views

app_name = "projects"
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<str:prjid>/', views.DetailView, name='detail'),
]
