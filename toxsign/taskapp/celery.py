import os
from celery import Celery
from django.apps import apps, AppConfig
from django.conf import settings

from django.utils.timezone import now
from datetime import timedelta
from celery.schedules import crontab


if not settings.configured:
    # set the default Django settings module for the 'celery' program.
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE", "config.settings.local"
    )  # pragma: no cover


app = Celery("toxsign")
# Using a string here means the worker will not have to
# pickle the object when using Windows.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")


class CeleryAppConfig(AppConfig):
    name = "toxsign.taskapp"
    verbose_name = "Celery Config"

    def ready(self):
        installed_apps = [app_config.name for app_config in apps.get_app_configs()]
        app.autodiscover_tasks(lambda: installed_apps, force=True)


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")  # pragma: no cover


@app.on_after_configure.connect
def cron_cleanup(sender, **kwargs):
    sender.add_periodic_task(
        crontab(hour=0, minute=0, day_of_week=1),
        cleanup_jobs.s(),
    )
    sender.add_periodic_task(
        crontab(hour=0, minute=0),
        cleanup_failed_jobs.s(),
    )

@app.task
def cleanup_jobs():
    from toxsign.jobs.models import Job
    # Clean anonymous jobs older than 7 days
    Job.objects.filter(updated_at__lte= now()-timedelta(days=7), created_by=None).delete()
    # Clean pending jobs?
    # Clean non-anonymous older than 2 months
    Job.objects.filter(updated_at__lte= now()-timedelta(months=2)).delete()

@app.task
def cleanup_failed_jobs():
    from toxsign.jobs.models import Job
    # Clean anonymous failed job older than 1 day
    Job.objects.filter(updated_at__lte= now()-timedelta(days=1), created_by=None, status="FAILURE").delete()
