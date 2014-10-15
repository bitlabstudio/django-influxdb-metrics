"""Utilities for working with influxdb."""
import copy
from threading import Thread

from django.conf import settings

from influxdb import client as influxdb


def apply_prefix_postfix(series_name, apply_prefix=True, apply_postfix=True):
    """
    Applies prefix or postfix to the given series name and returns it.

    :param series_name: String representing a series name.
    :param apply_prefix: If ``True``, the ``INFLUXDB_SERIES_PREFIX`` will be
      prepended to the ``series_name``.
    :param apply_postfix: If ``True``, the ``INFLUXDB_SERIES_POSTFIX`` will be
      appended to the ``series_name``.

    """
    prefix = ''
    if apply_prefix and getattr(settings, 'INFLUXDB_SERIES_PREFIX', False):
        prefix = settings.INFLUXDB_SERIES_PREFIX
    postfix = ''
    if apply_postfix and getattr(settings, 'INFLUXDB_SERIES_POSTFIX', False):
        postfix = settings.INFLUXDB_SERIES_POSTFIX
    full_series_name = '{0}{1}{2}'.format(prefix, series_name, postfix)
    return full_series_name


def apply_prefix_postfix_to_data(data, apply_prefix=True, apply_postfix=True):
    """
    Applies prefix or postfix to the given data dict and returns it.

    :param data: The datadict that you would pass to ``write_points``.
    :param apply_prefix: If ``True``, the ``INFLUXDB_SERIES_PREFIX`` will be
      prepended to the ``series_name``.
    :param apply_postfix: If ``True``, the ``INFLUXDB_SERIES_POSTFIX`` will be
      appended to the ``series_name``.

    """
    new_data = copy.deepcopy(data)
    for data_dict in new_data:
        data_dict['name'] = apply_prefix_postfix(
            data_dict['name'], apply_prefix, apply_postfix)
    return new_data


def get_db():
    """Returns an ``InfluxDBClient`` instance."""
    return influxdb.InfluxDBClient(
        settings.INFLUXDB_HOST,
        settings.INFLUXDB_PORT,
        settings.INFLUXDB_USER,
        settings.INFLUXDB_PASSWORD,
        settings.INFLUXDB_DATABASE,
    )


def query(query, time_precision='s', chunked=False):
    """Wrapper around ``InfluxDBClient.query()``."""
    db = get_db()
    return db.query(query, time_precision=time_precision, chunked=chunked)


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
    if getattr(settings, 'INFLUXDB_DISABLED', False):
        return

    if column_name is None:
        column_name = 'value'

    data = [{
        'name': series_name,
        'columns': [column_name, ],
        'points': [[value]], }]
    write_points(data)


def write_points(data, apply_prefix=True, apply_postfix=True):
    """
    Writes a series to influxdb.

    The ``data`` dict should look like this::

        data = [{
            'name': 'your.series.name',
            'columns': ['your_column_name', 'another_column', ],
            'points': [[value, another_value]], }]

    :param data: Dictionary with ``name``, ``columns`` and ``points``.
    :param apply_prefix: If ``True``, the ``INFLUXDB_SERIES_PREFIX`` will be
      prepended to the ``series_name``.
    :param apply_postfix: If ``True``, the ``INFLUXDB_SERIES_POSTFIX`` will be
      appended to the ``series_name``.

    """
    if getattr(settings, 'INFLUXDB_DISABLED', False):
        return

    db = get_db()
    new_data = copy.deepcopy(data)
    new_data = apply_prefix_postfix_to_data(data, apply_prefix, apply_postfix)
    thread = Thread(target=write_points_threaded, args=(db, new_data, ))
    thread.start()


def write_points_threaded(db, data):  # pragma: no cover
    """Method to be called via threading module."""
    try:
        db.write_points(data)
    except Exception, ex:
        if getattr(settings, 'INFLUXDB_FAIL_SILENTLY', True):
            pass
        else:
            raise ex
