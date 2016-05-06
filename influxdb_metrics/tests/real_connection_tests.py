"""Tests real connections with influxdb docker container."""
from django.contrib.auth.models import AnonymousUser
from django.test import TestCase, RequestFactory

from influxdb_metrics.utils import query, get_client

from ..middleware import InfluxDBRequestMiddleware


class RealConnectionTestCase(TestCase):
    """Tests sending real data to influxdb and testing results"""
    longMessage = True

    def setUp(self):
        self.influxdb_client = get_client()
        super(RealConnectionTestCase, self).setUp()

    def test_middleware(self):
        self.influxdb_client.delete_series(measurement='django_request')

        req = RequestFactory().get('/?campaign=bingo')
        req.META['HTTP_REFERER'] = 'http://google.co.uk/foobar/'
        req.user = AnonymousUser()
        mware = InfluxDBRequestMiddleware()
        mware.process_view(req, 'view_funx', 'view_args', 'view_kwargs')
        mware.process_exception(req, None)

        results = list(query('select * from django_request'))
        self.assertEqual(len(results), 1)
        result = results[0][0]
        self.assertEqual(result['value'], 0)
