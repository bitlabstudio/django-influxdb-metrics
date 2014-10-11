"""Tests for the ``influxdb_get_memcached_usage`` management command."""
from django.test import TestCase

from mock import patch

from ..management.commands.influxdb_get_memcached_usage import Command


class InfluxdbGetMemcachedUsageTestCase(TestCase):
    """Tests for the ``influxdb_get_memcached_usage`` management command."""
    longMessage = True

    def test_command(self):
        with patch(
                'influxdb_metrics.management.commands.'
                'influxdb_get_memcached_usage.write_points') as mock_write_points:
            cmd = Command()
            cmd.handle('foo')
            call_args = mock_write_points.call_args[0][0]
            self.assertEqual(
                call_args[0]['columns'],
                ['value', 'curr_items', ],
                msg=('Should construct a data dict with the correct columns'))
