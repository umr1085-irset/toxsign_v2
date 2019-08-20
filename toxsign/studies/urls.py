from django.urls import path
from toxsign.studies import views

app_name = "studies"
urlpatterns = [
    path('create/<str:prjid>/', views.CreateStudyView.as_view(), name='study_create'),
    path('edit/<str:stdid>/', views.EditStudyView.as_view(), name='study_edit'),
    path('<str:stdid>/', views.DetailView, name='detail')
]
