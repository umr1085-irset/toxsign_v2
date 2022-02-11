from django.urls import path
from toxsign.clusters import views

app_name = "clusters"
urlpatterns = [
    path('', views.index, name='index'),
    path('view/<str:type>/<str:clrid>/', views.details, name='details'),
    path('view_modal/<str:type>/<str:clrid>/', views.details_modal, name='details_modal'),
    path('graph/<str:type>/<str:clrid>/', views.get_graph_data, name='graph'),
]
