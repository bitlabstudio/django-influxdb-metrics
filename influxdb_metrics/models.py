"""Models and signal handlers for the influxdb_metrics app."""
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .utils import write_point


@receiver(user_logged_in)  # pragma: no cover
def user_logged_in_handler(sender, **kwargs):
    write_point('default.django.auth.user.login', value=1)


def user_post_delete_handler(sender, **kwargs):
    """Sends a metric to InfluxDB when a User object is deleted."""
    total = get_user_model().objects.all().count()
    write_point('default.django.auth.user.delete', value=1)
    write_point('default.django.auth.user.count', value=total)
post_delete.connect(user_post_delete_handler, sender=settings.AUTH_USER_MODEL)


def user_post_save_handler(**kwargs):
    """Sends a metric to InfluxDB when a new User object is created."""
    if kwargs.get('created'):
        total = get_user_model().objects.all().count()
        write_point('default.django.auth.user.create', value=1)
        write_point('default.django.auth.user.count', value=total)
post_save.connect(user_post_save_handler, sender=settings.AUTH_USER_MODEL)
