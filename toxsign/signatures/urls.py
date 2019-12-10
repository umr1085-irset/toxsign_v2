from django.urls import path, re_path
from toxsign.signatures import views

app_name = "signatures"
urlpatterns = [
    path('create/<str:prjid>', views.CreateSignatureView.as_view(), name='signature_create'),
    path('edit/<str:sigid>', views.EditSignatureView.as_view(), name='signature_edit'),
    re_path(r'^signature-autocomplete/$', views.SignatureToolAutocomplete.as_view(), name='signature-autocomplete'),
    path('<str:sigid>/', views.DetailView, name='detail'),
]
