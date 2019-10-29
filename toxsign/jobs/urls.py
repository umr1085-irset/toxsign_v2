from django.urls import path
from toxsign.jobs import views


app_name = 'jobs'
# Define urls here
urlpatterns = [
    # ex: /jobs/
    path('running_jobs/', views.RunningJobsView.as_view(), name='running_jobs'),
    path('delete_job/<int:pk>', views.Delete_job, name='delete_job'),
    # ex: /jobs/5/
    # the 'name' value as called by the {% url %} template tag
    path('<int:pk>/result', views.DetailView, name='results'),
    path('<int:pk>/result/<str:file_name>', views.DownloadView, name='results_download'),
]
