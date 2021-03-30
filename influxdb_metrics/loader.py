"""Loads celery or non-celery version."""
from functools import lru_cache

from django.conf import settings

try:
    from .tasks import write_points as write_points_celery
except ImportError:
    write_points_celery = None

from .utils import write_points as write_points_normal

write_points = None
if getattr(settings, 'INFLUXDB_USE_CELERY', False):
    write_points = write_points_celery.delay
else:
    write_points = write_points_normal


@lru_cache(maxsize=32)
def measurement_name_for(measurement: str) -> str:
    """ Allow a configurable prefix for InfluxDB measurement names

        Default (no INFLUXDB_PREFIX setting):              'django_request'
        Custom Prefix (INFLUXDB_PREFIX="app"):                'app_request'
        Empty Prefix (INFLUXDB_PREFIX="", INFLUXDB_PREFIX=None):  'request'

    """
    prefix = getattr(settings, 'INFLUXDB_PREFIX', 'django')
    prefix = prefix if prefix else ""   # Replace None with ""
    sep = "_" if prefix else ""
    return '{}{}{}'.format(prefix, sep, measurement)
