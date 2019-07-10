from django.urls import path
from toxsign.signatures import views

app_name = "signatures"
urlpatterns = [
    path('create/<str:assid>', views.CreateView.as_view(), name='signature_create'),
    path('<str:sigid>/', views.DetailView, name='detail'),
]
