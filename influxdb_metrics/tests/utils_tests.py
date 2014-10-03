"""Tests for the utils module of the influxdb_metrics app."""
import copy

from django.test import TestCase

from mock import patch

from .. import utils
reload(utils)


class ApplyPrefixPostfixTestCase(TestCase):
    """Tests for the ``apply_prefix_postfix`` method."""
    longMessage = True

    def test_method(self):
        result = utils.apply_prefix_postfix('foobar')
        self.assertEqual(result, 'pre.foobar.post', msg=(
            'Should apply prefix and postfix by default'))

        result = utils.apply_prefix_postfix('foobar', False)
        self.assertEqual(result, 'foobar.post', msg=(
            'Should not apply prefix if set to `False`'))

        result = utils.apply_prefix_postfix('foobar', False, False)
        self.assertEqual(result, 'foobar', msg=(
            'Should not apply postfix if set to `False`'))


class ApplyPrefixPostfixToDataTestCase(TestCase):
    """Tests for the ``apply_prefix_postfix_to_data`` method."""
    longMessage = True

    def test_method(self):
        data = [
            {'name': 'foobar', },
            {'name': 'barfoo', }
        ]
        backup = copy.deepcopy(data)
        expected = [
            {'name': 'pre.foobar.post', },
            {'name': 'pre.barfoo.post', }
        ]

        result = utils.apply_prefix_postfix_to_data(data)
        self.assertEqual(data, backup, msg=(
            'Should not alter the original data dict'))
        self.assertEqual(result, expected, msg=(
            'Should apply prefix and postix to all items in the data dict'))


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
                  'name': 'foobar',
                  'columns': ['value']}],
                msg=('Should set column_name to `value`'))

            utils.write_point('foobar', column_name='count', value=1)
            self.assertEqual(
                mock_write_points.call_args[0][0],
                [{'points': [[1]],
                  'name': 'foobar',
                  'columns': ['count']}],
                msg=('Should set column_name to given value'))


class WritePointsTestCase(TestCase):
    """Tests for the ``write_points`` method."""
    longMessage = True

    def test_method(self):
        with patch('influxdb_metrics.utils.get_db') as mock_get_db:
            data = [{'name': 'series.name', }]
            utils.write_points(data, False, False)
            self.assertEqual(
                mock_get_db.return_value.write_points.call_args[0][0],
                data,
                msg=('Should instantiate a client and call the `write_points`'
                     ' method of that client and should pass in the given'
                     ' data'))

            new_data = utils.apply_prefix_postfix_to_data(data)
            utils.write_points(data)
            self.assertEqual(
                mock_get_db.return_value.write_points.call_args[0][0],
                new_data,
                msg=('Should apply prefix and postfix to the whole data dict'))
