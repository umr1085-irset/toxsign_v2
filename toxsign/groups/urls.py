from django.urls import path
from toxsign.projects import views

app_name = "groups"
urlpatterns = [
    path('<str:grpid>/', views.DetailView, name='detail'),
]
