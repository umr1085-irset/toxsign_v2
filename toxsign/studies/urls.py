from django.urls import path
from toxsign.projects import views

app_name = "studies"
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<str:stdid>/', views.DetailView, name='detail'),
]
