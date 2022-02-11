from django.apps import AppConfig


class GroupsAppConfig(AppConfig):

    name = "toxsign.groups"
    verbose_name = "Groups"

    def ready(self):
        try:
            import groups.signals  # noqa F401
        except ImportError:
            pass
