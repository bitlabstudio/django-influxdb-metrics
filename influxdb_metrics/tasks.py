"""Celery tassk for the influxdb_metrics app."""
from __future__ import absolute_import

from celery import shared_task

from .utils import write_points as write_points_normal


@shared_task
def write_points(data, name='influxdb_metrics.tasks.write_points'):
    """
    Wrapper around `utils.write_points`.

    If you use this, make sure to set `INFLUXDB_USE_THREADING = False`

    """
    write_points_normal(data, force_disable_threading=True)
