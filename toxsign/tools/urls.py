from django.urls import path
from toxsign.tools import views

app_name = 'tools'
# Define urls here
urlpatterns = [
    # ex: /tools/
    path('', views.IndexView.as_view(), name='index'),
    path('dist/results/<int:job_id>', views.distance_analysis_results, name='run_dist_results'),
    path('dist/results/<int:job_id>/table', views.distance_analysis_table, name='run_dist_table'),
    path('enrich/results/<int:job_id>', views.functional_analysis_results, name='run_enrich_results'),
    path('predict/results/<int:job_id>', views.prediction_tool_results, name='run_predict_results'),
    path('cluster_dist/results/<int:job_id>', views.cluster_dist_results, name='run_cluster_dist_results'),
    path('enrich/results/<int:job_id>/table', views.functional_analysis_full_table, name='run_enrich_table_full'),
    path('enrich/results/<int:job_id>/table/<str:type>', views.functional_analysis_partial_table, name='run_enrich_table_partial'),
    path('dist/', views.distance_analysis_tool, name='run_dist'),
    path('enrich/', views.functional_analysis_tool, name='run_enrich'),
    path('cluster_dist/', views.cluster_dist_tool, name='run_cluster_dist'),
    path('predict/', views.prediction_tool, name='run_predict'),
]
