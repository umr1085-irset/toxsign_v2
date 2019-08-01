from django.urls import path
from toxsign.assays import views

app_name = "assays"
urlpatterns = [
    path('create/assay/<str:prjid>', views.AssayCreateView.as_view(), name='assay_create'),
    path('create/factor/<str:prjid>', views.FactorCreateView.as_view(), name='factor_create'),
    path('<str:assid>/', views.DetailView, name='detail'),
]
