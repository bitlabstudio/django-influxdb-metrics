"""Tests for the utils module of the influxdb_metrics app."""
from django.test import TestCase

from mock import patch

from .. import utils


class GetClientTestCase(TestCase):
    """Tests for the ``get_client`` method."""
    longMessage = True

    def test_method(self):
        with patch('influxdb_metrics.utils.InfluxDBClient'):
            result = utils.get_client()
            self.assertTrue('InfluxDBClient()' in str(result))


class QueryTestCase(TestCase):
    """Tests for the ``query`` method."""
    longMessage = True

    def test_method(self):
        with patch('influxdb_metrics.utils.get_client'):
            result = utils.query('foo')
            self.assertTrue('get_client().query()' in str(result), msg=(
                'Calls `.query()` on the db instance'))


class WritePointsTestCase(TestCase):
    """Tests for the ``write_points`` method."""
    longMessage = True

    def setUp(self):
        super(WritePointsTestCase, self).setUp()
        self.patch_get_client = patch('influxdb_metrics.utils.get_client')
        self.patch_thread = patch('influxdb_metrics.utils.Thread')
        self.mock_get_client = self.patch_get_client.start()
        self.mock_thread = self.patch_thread.start()

    def tearDown(self):
        super(WritePointsTestCase, self).tearDown()
        self.patch_get_client.stop()
        self.patch_thread.stop()

    def test_method(self):
        data = [{
            'measurement': 'series.name',
        }]

        with self.settings(INFLUXDB_USE_THREADING=True):
            utils.write_points(data)
            self.assertEqual(
                self.mock_thread.call_args[1]['args'][1],
                data,
                msg=('Should instantiate a client and call the `write_points`'
                     ' method of that client and should pass in the given'
                     ' data'))

        with self.settings(INFLUXDB_DISABLED=True):
            result = utils.write_points([])
            self.assertEqual(result, None, msg=(
                'If setting is set, should return immediately'))
