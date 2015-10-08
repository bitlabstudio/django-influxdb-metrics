"""Utilities for working with influxdb."""
import copy
from threading import Thread

from django.conf import settings

from influxdb import InfluxDBClient


def get_client():
    """Returns an ``InfluxDBClient`` instance."""
    return InfluxDBClient(
        settings.INFLUXDB_HOST,
        settings.INFLUXDB_PORT,
        settings.INFLUXDB_USER,
        settings.INFLUXDB_PASSWORD,
        settings.INFLUXDB_DATABASE,
    )


def query(query, time_precision='s', chunked=False):
    """Wrapper around ``InfluxDBClient.query()``."""
    client = get_client()
    return client.query(query, time_precision=time_precision, chunked=chunked)


def write_points(data):
    """
    Writes a series to influxdb.

    :param data: Array of dicts, as required by
      https://github.com/influxdb/influxdb-python

    """
    if getattr(settings, 'INFLUXDB_DISABLED', False):
        return

    client = get_client()
    thread = Thread(target=write_points_threaded, args=(client, data, ))
    thread.start()


def write_points_threaded(client, data):  # pragma: no cover
    """Method to be called via threading module."""
    try:
        client.write_points(data)
    except Exception, ex:
        if getattr(settings, 'INFLUXDB_FAIL_SILENTLY', True):
            pass
        else:
            raise ex
