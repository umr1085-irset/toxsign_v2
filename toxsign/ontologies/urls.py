from django.urls import path
from toxsign.ontologies import views

app_name = "ontologies"
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<int:pk>/', views.DetailView.as_view(), name='detail'),
]
