from django.urls import path
from toxsign.assays import views

app_name = "assays"
urlpatterns = [
    path('create/assay/<str:stdid>', views.AssayCreateView.as_view(), name='assay_create'),
    path('create/factor/<str:assid>', views.FactorCreateView.as_view(), name='factor_create'),
    path('<str:assid>/', views.DetailView, name='detail'),
]
