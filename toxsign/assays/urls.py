from django.urls import path
from toxsign.assays import views

app_name = "assays"
urlpatterns = [
    path('create/assay/<str:prjid>', views.AssayCreateView.as_view(), name='assay_create'),
    path('create/factor/<str:prjid>', views.FactorCreateView.as_view(), name='factor_create'),
    path('factor/<str:facid>/', views.FactorDetailView, name='factor_detail'),
    path('<str:assid>/', views.AssayDetailView, name='assay_detail'),
]
