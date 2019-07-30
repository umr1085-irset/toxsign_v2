from django.urls import path

from toxsign.users.views import (
    user_list_view,
    user_redirect_view,
    user_update_view,
    user_detail_view,
    dismiss_notification,
    accept_group_invitation
)

app_name = "users"
urlpatterns = [
    path("", view=user_list_view, name="list"),
    path("~redirect/", view=user_redirect_view, name="redirect"),
    path("~update/", view=user_update_view, name="update"),
    path("<str:username>/", view=user_detail_view, name="detail"),
    path("notification/dismiss/<int:notification_id>", view=dismiss_notification, name="dismiss_notification"),
    path("notification/accept/<int:notification_id>", view=accept_group_invitation, name="accept_group_invitation"),
]
