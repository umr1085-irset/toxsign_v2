from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth import get_user_model

from toxsign.groups.models import Ownership

class GroupOwnershipAdmin(admin.ModelAdmin):
    list_display = ['group', 'owner']

admin.site.register(Ownership, GroupOwnershipAdmin)
