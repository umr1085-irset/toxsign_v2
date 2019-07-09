from django.urls import path
from toxsign.assays import views

app_name = "assays"
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<str:assid>/', views.DetailView, name='detail'),
]
