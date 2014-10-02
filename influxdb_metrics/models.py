"""Models and signal handlers for the influxdb_metrics app."""
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in, user_login_failed
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .utils import write_point


@receiver(user_logged_in)  # pragma: no cover
def user_logged_in_handler(sender, **kwargs):
    write_point('default.django.auth.user.login', value=1)


@receiver(user_login_failed)  # pragma: no cover
def user_login_failed_handler(sender, **kwargs):
    write_point('default.django.auth.user.login.failed', value=1)


@receiver(post_delete, sender=User)  # pragma: no cover
def user_post_delete_handler(sender, **kwargs):
    """Sends a metric to InfluxDB when a User object is deleted."""
    total = User.objects.all().count()
    write_point('default.django.auth.user.delete', value=1)
    write_point('default.django.auth.user.count', value=total)


@receiver(post_save, sender=User)  # pragma: no cover
def user_post_save_handler(sender, **kwargs):
    """Sends a metric to InfluxDB when a new User object is created."""
    if kwargs.get('created'):
        total = User.objects.all().count()
        write_point('default.django.auth.user.create', value=1)
        write_point('default.django.auth.user.count', value=total)
