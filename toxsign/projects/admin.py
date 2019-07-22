from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth import get_user_model

from toxsign.projects.models import Project
class ProjectAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['name', 'read_groups', 'edit_groups', 'created_by', 'status', 'description']}),
    ]
    list_display = ['name', 'created_at', 'updated_at']
    search_fields = ['name']


admin.site.register(Project, ProjectAdmin)
