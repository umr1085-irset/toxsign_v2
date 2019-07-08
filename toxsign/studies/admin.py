from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth import get_user_model

from toxsign.studies.models import Study
class StudyAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['name', 'created_by', 'status', 'description', 'study_type', 'experimental_design', 'results', 'project']}),
    ]
    list_display = ['name', 'created_at', 'updated_at']
    search_fields = ['name']

admin.site.register(Study, StudyAdmin)
