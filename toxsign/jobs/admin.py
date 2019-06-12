from django.contrib import admin
from .models import Job

# Register your models here.
class JobsAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['title', 'created_by', 'output', 'status', 'running_tool', 'celery_task_id']}),
    ]
    list_display = ['title', 'created_at', 'updated_at']
    list_filter = ['created_at']
    search_fields = ['title']

admin.site.register(Job, JobsAdmin)
