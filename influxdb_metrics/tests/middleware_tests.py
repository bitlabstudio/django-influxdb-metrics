"""Tests for the middlewares of the influxdb_metrics app."""
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser, User

from mock import patch

from ..middleware import InfluxDBRequestMiddleware


class InfluxDBRequestMiddlewareTestCase(TestCase):
    """Tests for the ``InfluxDBRequestMiddleware`` middleware."""
    longMessage = True

    def setUp(self):
        super(InfluxDBRequestMiddlewareTestCase, self).setUp()
        self.patch_write_points = patch(
            'influxdb_metrics.middleware.write_points')
        self.patch_write_point = patch(
            'influxdb_metrics.models.write_point')
        self.mock_write_points = self.patch_write_points.start()
        self.mock_write_point = self.patch_write_point.start()
        self.staff = User.objects.create(username='staff', is_staff=True)
        self.superuser = User.objects.create(
            username='superuser', is_superuser=True)

    def tearDown(self):
        super(InfluxDBRequestMiddlewareTestCase, self).tearDown()
        self.patch_write_points.stop()
        self.patch_write_point.stop()

    def test_middleware(self):
        req = RequestFactory().get('/')
        req.META['HTTP_REFERER'] = 'http://google.co.uk/foobar/'
        req.user = AnonymousUser()
        mware = InfluxDBRequestMiddleware()
        mware.process_view(req, 'view_funx', 'view_args', 'view_kwargs')
        mware.process_exception(req, None)
        self.assertEqual(
            self.mock_write_points.call_args[0][0][0]['points'][0][9],
            'google.co.uk',
            msg=('Should correctly determine referer_tld'))

        req = RequestFactory().get('/')
        req.META['HTTP_REFERER'] = 'http://google.co.uk/foobar/'
        req.user = self.staff
        mware = InfluxDBRequestMiddleware()
        mware.process_view(req, 'view_funx', 'view_args', 'view_kwargs')
        mware.process_response(req, None)
        self.assertEqual(
            self.mock_write_points.call_args[0][0][0]['points'][0][9],
            'google.co.uk',
            msg=('Should also work for successful responses'))

        req = RequestFactory().get('/', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        req.META['HTTP_REFERER'] = 'http://google.co.uk/foobar/'
        req.user = self.superuser
        mware = InfluxDBRequestMiddleware()
        mware.process_view(req, 'view_funx', 'view_args', 'view_kwargs')
        mware.process_response(req, None)
        self.assertEqual(
            self.mock_write_points.call_args[0][0][0]['points'][0][9],
            'google.co.uk',
            msg=('Should also work for ajax requests'))
