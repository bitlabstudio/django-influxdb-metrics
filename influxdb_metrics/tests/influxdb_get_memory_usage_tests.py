"""Tests for the ``influxdb_get_memory_usage`` management command."""
from django.test import TestCase

from mock import patch

from ..management.commands.influxdb_get_memory_usage import Command


class InfluxdbGetMemoryUsageTestCase(TestCase):
    """Tests for the ``influxdb_get_memory_usage`` management command."""
    longMessage = True

    def test_command(self):
        with patch(
                'influxdb_metrics.management.commands.'
                'influxdb_get_memory_usage.write_points') as mock_write_points:
            cmd = Command()
            cmd.handle()
            call_args = mock_write_points.call_args[0][0]
            self.assertEqual(
                call_args[0]['columns'],
                ['value', 'largest_process', 'largest_process_name'],
                msg=('Should construct a data dict with the correct columns'))

            cmd.handle('foobar')
            call_args = mock_write_points.call_args[0][0]
            self.assertTrue(call_args, msg=(
                'Should also work when a username is given'))
