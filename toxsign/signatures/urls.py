from django.urls import path
from toxsign.signatures import views

app_name = "signatures"
urlpatterns = [
    path('<str:sigid>/', views.DetailView.as_view(), name='detail'),
]
