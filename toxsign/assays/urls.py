from django.urls import path
from toxsign.assays import views

app_name = "assays"
urlpatterns = [
    path('<str:assid>/', views.DetailView, name='detail'),
]
