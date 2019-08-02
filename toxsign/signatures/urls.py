from django.urls import path
from toxsign.signatures import views

app_name = "signatures"
urlpatterns = [
    path('create/<str:prjid>', views.CreateSignatureView.as_view(), name='signature_create'),
    path('edit/<str:sigid>', views.EditSignatureView.as_view(), name='signature_edit'),
    path('<str:sigid>/', views.DetailView, name='detail'),
]
