from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth import get_user_model

from toxsign.superprojects.models import Superproject

class SuperprojectAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['name', 'created_by', 'description']}),
    ]
    list_display = ['name', 'created_at', 'updated_at']
    search_fields = ['name']


admin.site.register(Superproject, SuperprojectAdmin)
