"""Middlewares for the influxdb_metrics app."""

from django import VERSION as DJANGO_VERSION
import inspect
import time
import logging
try:
    from urllib import parse
except ImportError:
    import urlparse as parse

from django.conf import settings
from django.core.exceptions import MiddlewareNotUsed
try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError:
    class MiddlewareMixin(object):
        pass

from tld import get_tld
from tld.exceptions import TldBadUrl, TldDomainNotFound, TldIOError

from .loader import measurement_name_for, write_points

if DJANGO_VERSION < (1, 10):
    def is_user_authenticated(user):
        return user.is_authenticated()
else:
    def is_user_authenticated(user):
        return user.is_authenticated

logger = logging.getLogger(__name__)


class InfluxDBRequestMiddleware(MiddlewareMixin):
    """
    Measures request time and sends metric to InfluxDB.

    Credits go to: https://github.com/andymckay/django-statsd/blob/master/django_statsd/middleware.py#L24  # NOQA

    """

    def __init__(self, get_response=None):
        if getattr(settings, 'INFLUXDB_DISABLED', False):
            raise MiddlewareNotUsed
        super().__init__(get_response=get_response)

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
        self._record_time(request)
        return response

    def process_exception(self, request, exception):
        self._record_time(request)

    def _record_time(self, request):
        if hasattr(request, '_start_time'):
            ms = int((time.time() - request._start_time) * 1000)
            if request.is_ajax():
                is_ajax = True
            else:
                is_ajax = False

            is_authenticated = False
            is_staff = False
            is_superuser = False
            if is_user_authenticated(request.user):
                is_authenticated = True
                if request.user.is_staff:
                    is_staff = True
                if request.user.is_superuser:
                    is_superuser = True

            referer = request.META.get('HTTP_REFERER')
            referer_tld = None
            referer_tld_string = ''
            if referer:
                try:
                    referer_tld = get_tld(referer, as_object=True)
                except (TldBadUrl, TldDomainNotFound, TldIOError):
                    pass
            if referer_tld:
                referer_tld_string = referer_tld.tld

            url = request.get_full_path()
            url_query = parse.parse_qs(parse.urlparse(url).query)

            # This allows you to measure click rates for ad-campaigns, just
            # make sure that your ads have `?campaign=something` in the URL
            campaign_keyword = getattr(
                settings, 'INFLUXDB_METRICS_CAMPAIGN_KEYWORD', 'campaign')
            campaign = ''
            if campaign_keyword in url_query:
                campaign = url_query[campaign_keyword][0]

            data = [{
                'measurement': measurement_name_for('request'),
                'tags': {
                    'host': settings.INFLUXDB_TAGS_HOST,
                    'is_ajax': is_ajax,
                    'is_authenticated': is_authenticated,
                    'is_staff': is_staff,
                    'is_superuser': is_superuser,
                    'method': request.method,
                    'module': request._view_module,
                    'view': request._view_name,
                    'referer': referer,
                    'referer_tld': referer_tld_string,
                    'full_path': url,
                    'path': request.path,
                    'campaign': campaign,
                },
                'fields': {'value': ms, },
            }]
            try:
                write_points(data)
            except Exception as err:
                logger.exception(err, extra={"request": request})
                # sadly, when using celery, there can be issues with the connection to the MQ. Better to drop the data
                # than fail the request.
                pass
