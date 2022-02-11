from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth import get_user_model

from toxsign.users.forms import UserChangeForm, UserCreationForm
from toxsign.users.models import Notification

User = get_user_model()


@admin.register(User)
class UserAdmin(auth_admin.UserAdmin):

    form = UserChangeForm
    add_form = UserCreationForm
    fieldsets = (("User", {"fields": [("name",), ("last_name",), ("institut",), ("projects",)]}),) + auth_admin.UserAdmin.fieldsets
    list_display = ["username", "name", "last_name", "institut", "is_superuser"]
    search_fields = ["name"]

class NotificationAdmin(admin.ModelAdmin):
    pass

admin.site.register(Notification, NotificationAdmin)
