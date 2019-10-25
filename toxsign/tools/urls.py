from django.urls import path
from toxsign.tools import views

app_name = 'tools'
# Define urls here
urlpatterns = [
    # ex: /tools/
    path('', views.IndexView.as_view(), name='index'),
    path('dist/results/<int:job_id>', views.distance_analysis_results, name='run_dist_results'),
    path('dist/results/<int:job_id>/table', views.distance_analysis_table, name='run_dist_results_table'),
    path('enrich/results/<int:job_id>', views.functional_analysis_results, name='run_enrich_results'),
    path('dist/', views.distance_analysis_tool, name='run_dist'),
    path('enrich/', views.functional_analysis_tool, name='run_enrich'),
    path('<int:toolid>/', views.DetailView, name='detail'),
]
