from django.urls import path
from toxsign.studies import views

app_name = "studies"
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<str:stdid>/', views.DetailView, name='detail'),
    path('study_edit/<int:pk>/', views.EditView.as_view(), name='study_edit'),
]
