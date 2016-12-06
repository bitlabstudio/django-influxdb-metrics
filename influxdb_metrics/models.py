"""Models and signal handlers for the influxdb_metrics app."""
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .loader import write_points


@receiver(user_logged_in)  # pragma: no cover
def user_logged_in_handler(sender, **kwargs):
    data = [{
        'measurement': 'django_auth_user_login',
        'tags': {'host': settings.INFLUXDB_TAGS_HOST, },
        'fields': {'value': 1, },
        'time': timezone.now().isoformat(),
    }]
    write_points(data)


def user_post_delete_handler(sender, **kwargs):
    """Sends a metric to InfluxDB when a User object is deleted."""
    total = get_user_model().objects.all().count()
    data = [{
        'measurement': 'django_auth_user_delete',
        'tags': {'host': settings.INFLUXDB_TAGS_HOST, },
        'fields': {'value': 1, },
        'time': timezone.now().isoformat(),
    }]
    write_points(data)

    data = [{
        'measurement': 'django_auth_user_count',
        'tags': {'host': settings.INFLUXDB_TAGS_HOST, },
        'fields': {'value': total, },
        'time': timezone.now().isoformat(),
    }]
    write_points(data)


post_delete.connect(user_post_delete_handler, sender=settings.AUTH_USER_MODEL)


def user_post_save_handler(**kwargs):
    """Sends a metric to InfluxDB when a new User object is created."""
    if kwargs.get('created'):
        total = get_user_model().objects.all().count()
        data = [{
            'measurement': 'django_auth_user_create',
            'tags': {'host': settings.INFLUXDB_TAGS_HOST, },
            'fields': {'value': 1, },
            'time': timezone.now().isoformat(),
        }]
        write_points(data)

        data = [{
            'measurement': 'django_auth_user_count',
            'tags': {'host': settings.INFLUXDB_TAGS_HOST, },
            'fields': {'value': total, },
            'time': timezone.now().isoformat(),
        }]
        write_points(data)


post_save.connect(user_post_save_handler, sender=settings.AUTH_USER_MODEL)
