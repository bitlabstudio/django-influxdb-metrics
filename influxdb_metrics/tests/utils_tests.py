"""Tests for the utils module of the influxdb_metrics app."""
from django.test import TestCase

from mock import patch

from .. import utils


class GetDBTestCase(TestCase):
    """Tests for the ``get_db`` method."""
    longMessage = True

    def test_method(self):
        with patch('influxdb_metrics.utils.influxdb'):
            result = utils.get_db()
            self.assertTrue('influxdb.InfluxDBClient()' in str(result))


class WritePointTestCase(TestCase):
    """Tests for the ``write_point`` method."""
    longMessage = True

    def test_method(self):
        with patch('influxdb_metrics.utils.write_points') as mock_write_points:
            utils.write_point('foobar', value=1)
            self.assertEqual(
                mock_write_points.call_args[0][0],
                [{'points': [[1]],
                  'name': 'pre.foobar.post',
                  'columns': ['value']}],
                msg=('Should set column_name to `value` and apply prefix and'
                     ' postfix to `series_name`'))

            utils.write_point('foobar', column_name='count', value=1)
            self.assertEqual(
                mock_write_points.call_args[0][0],
                [{'points': [[1]],
                  'name': 'pre.foobar.post',
                  'columns': ['count']}],
                msg=('Should set column_name to given value'))

            utils.write_point('foobar', value=1, apply_prefix=False)
            self.assertEqual(
                mock_write_points.call_args[0][0],
                [{'points': [[1]],
                  'name': 'foobar.post',
                  'columns': ['value']}],
                msg=('Should not apply prefix if set to `False`'))

            utils.write_point('foobar', value=1, apply_postfix=False)
            self.assertEqual(
                mock_write_points.call_args[0][0],
                [{'points': [[1]],
                  'name': 'pre.foobar',
                  'columns': ['value']}],
                msg=('Should not apply postfix if set to `False`'))


class WritePointsTestCase(TestCase):
    """Tests for the ``write_points`` method."""
    longMessage = True

    def test_method(self):
        with patch('influxdb_metrics.utils.get_db') as mock_get_db:
            data = [{'test': 1, }]
            utils.write_points([{'test': 1, }])
            self.assertEqual(
                mock_get_db.return_value.write_points.call_args[0][0],
                data,
                msg=('Should instantiate a client and call the `write_points`'
                     ' method of that client and should pass in the given'
                     ' data'))
