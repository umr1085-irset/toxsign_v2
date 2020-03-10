from django.urls import path
from toxsign.clusters import views

app_name = "clusters"
urlpatterns = [
    path('', views.index, name='index'),
    path('view/<int:clrid>/', views.details, name='details'),
    path('graph/<int:clrid>/', views.get_graph_data, name='graph'),
]
