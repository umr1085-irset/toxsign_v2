from django.urls import path
from toxsign.signatures import views

app_name = "signatures"
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('<str:sigid>/', views.DetailView.as_view(), name='detail'),
]
