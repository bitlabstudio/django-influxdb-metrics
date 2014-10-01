"""Utilities for working with influxdb."""
from django.conf import settings

from influxdb import client as influxdb


def get_db():
    """Returns an ``InfluxDBClient`` instance."""
    return influxdb.InfluxDBClient(
        settings.INFLUXDB_HOST,
        settings.INFLUXDB_PORT,
        settings.INFLUXDB_USER,
        settings.INFLUXDB_PASSWORD,
        settings.INFLUXDB_DATABASE,
    )


def write_point(series_name, column_name=None, value=None, apply_prefix=True,
                apply_postfix=True):
    """
    Writes a series whith only one column.

    :param series_name: String representing the name of the series.
    :param column_name: String representing the column name. If ``None``
      (default), the column name will be set to ``value``.
    :param value: Value of the metric.
    :param apply_prefix: If ``True``, the ``INFLUXDB_SERIES_PREFIX`` will be
      prepended to the ``series_name``.
    :param apply_postfix: If ``True``, the ``INFLUXDB_SERIES_POSTFIX`` will be
      appended to the ``series_name``.

    """
    if column_name is None:
        column_name = 'value'

    prefix = ''
    if apply_prefix and getattr(settings, 'INFLUXDB_SERIES_PREFIX', False):
        prefix = settings.INFLUXDB_SERIES_PREFIX
    postfix = ''
    if apply_postfix and getattr(settings, 'INFLUXDB_SERIES_POSTFIX', False):
        postfix = settings.INFLUXDB_SERIES_POSTFIX
    full_series_name = '{0}{1}{2}'.format(prefix, series_name, postfix)

    data = [{
        'name': full_series_name,
        'columns': [column_name, ],
        'points': [[value]], }]
    write_points(data)


def write_points(data):
    """
    Writes a series to influxdb.

    The ``data`` dict should look like this::

        data = [{
            'name': 'your.series.name',
            'columns': ['your_column_name', 'another_column', ],
            'points': [[value, another_value]], }]

    :param data: Dictionary with ``name``, ``columns`` and ``points``.

    """
    db = get_db()
    db.write_points(data)
