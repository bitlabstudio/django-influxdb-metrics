"""Middlewares for the influxdb_metrics app."""
import os
import datetime
import inspect
import time

from django.conf import settings

from .metrics_utils import METRICS
from .loader import write_points


def _write_metrics(data, obj, metrics):
    for m in metrics:
        attr = getattr(obj, m, None) if hasattr(obj, m) else obj.get(m)
        value = attr() if callable(attr) else  attr
        data[m] = value
        if METRICS.has_key(m):
            data.update(METRICS[m](value))

class InfluxDBRequestMiddleware(object):
    """
    Measures request time and sends metric to InfluxDB.

    Credits go to: https://github.com/andymckay/django-statsd/blob/master/django_statsd/middleware.py#L24  # NOQA

    """
    def process_view(self, request, view_func, view_args, view_kwargs):
        view = view_func
        if not inspect.isfunction(view_func):
            view = view.__class__
        try:
            request._view_module = view.__module__
            request._view_name = view.__name__
            request._start_time = time.time()
        except AttributeError:  # pragma: no cover
            pass

    def process_response(self, request, response):
        self._record_time(request, response)
        return response

    def process_exception(self, request, exception):
        self._record_time(request, {'status_code':500})

    def _record_time(self, request, response):
        if not hasattr(request, '_start_time'):
            return
        
        ms = int((time.time() - request._start_time) * 1000)
        tags = {'host':os.uname()[1]}
        _write_metrics(tags, request, settings.INFLUX_REQUEST_METRICS)
        _write_metrics(tags, request.META, settings.INFLUX_HEADER_METRICS)
        if response:
            _write_metrics(tags, response, settings.INFLUX_RESPONSE_METRICS)
            
        if request.user.is_authenticated():
            user = request.user
            _write_metrics(tags, user, settings.INFLUX_USER_METRICS)

        data = [{
            'measurement': 'django_request',
            'tags': tags,
            'fields': {'value': ms, },
            'time': datetime.datetime.utcnow().isoformat()
        }]
        write_points(data)
