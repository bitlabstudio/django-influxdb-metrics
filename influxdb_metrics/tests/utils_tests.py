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


class QueryTestCase(TestCase):
    """Tests for the ``query`` method."""
    longMessage = True

    def test_method(self):
        with patch('influxdb_metrics.utils.get_db'):
            result = utils.query('foo')
            self.assertTrue('get_db().query()' in str(result), msg=(
                'Calls `.query()` on the db instance'))


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

        with self.settings(INFLUXDB_DISABLED=True):
            result = utils.write_point('foobar', value=1)
            self.assertEqual(result, None, msg=(
                'If setting is set, should return immediately'))


class WritePointsTestCase(TestCase):
    """Tests for the ``write_points`` method."""
    longMessage = True

    def setUp(self):
        super(WritePointsTestCase, self).setUp()
        self.patch_get_db = patch('influxdb_metrics.utils.get_db')
        self.patch_thread = patch('influxdb_metrics.utils.Thread')
        self.mock_get_db = self.patch_get_db.start()
        self.mock_thread = self.patch_thread.start()

    def tearDown(self):
        super(WritePointsTestCase, self).tearDown()
        self.patch_get_db.stop()
        self.patch_thread.stop()

    def test_method(self):
        data = [{'name': 'series.name', }]
        utils.write_points(data, False, False)
        self.assertEqual(
            self.mock_thread.call_args[1]['args'][1],
            data,
            msg=('Should instantiate a client and call the `write_points`'
                 ' method of that client and should pass in the given'
                 ' data'))

        new_data = utils.apply_prefix_postfix_to_data(data)
        utils.write_points(data)
        self.assertEqual(
            self.mock_thread.call_args[1]['args'][1],
            new_data,
            msg=('Should apply prefix and postfix to the whole data dict'))

        with self.settings(INFLUXDB_DISABLED=True):
            result = utils.write_points([])
            self.assertEqual(result, None, msg=(
                'If setting is set, should return immediately'))
