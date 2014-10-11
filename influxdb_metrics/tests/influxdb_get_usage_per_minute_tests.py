"""Tests for the ``influxdb_get_usage_per_minute`` management command."""
from django.test import TestCase

from mock import patch

from ..management.commands.influxdb_get_usage_per_minute import Command


class InfluxdbGetUsagePerMinuteTestCase(TestCase):
    """Tests for the ``influxdb_get_usage_per_minute`` management command."""
    longMessage = True

    def setUp(self):
        super(InfluxdbGetUsagePerMinuteTestCase, self).setUp()
        self.patch_write_points_cpu = patch(
            'influxdb_metrics.management.commands.influxdb_get_cpu_usage.'
            'write_points')
        self.patch_write_points_memory = patch(
            'influxdb_metrics.management.commands.influxdb_get_memory_usage.'
            'write_points')
        self.patch_write_points_memcached = patch(
            'influxdb_metrics.management.commands.'
            'influxdb_get_memcached_usage.write_points')
        self.mock_write_points_cpu = self.patch_write_points_cpu.start()
        self.mock_write_points_memory = self.patch_write_points_memory.start()
        self.mock_write_points_memcached = \
            self.patch_write_points_memcached.start()

    def tearDown(self):
        super(InfluxdbGetUsagePerMinuteTestCase, self).tearDown()
        self.patch_write_points_cpu.stop()
        self.patch_write_points_memory.stop()
        self.patch_write_points_memcached.stop()

    def test_command(self):
        cmd = Command()
        cmd.handle('foo', 'bar', 'foobar')
        self.assertTrue(self.mock_write_points_cpu.called, msg=(
            'Should call the get cpu Command'))
        self.assertTrue(self.mock_write_points_memory.called, msg=(
            'Should call the get memory Command'))
        self.assertTrue(self.mock_write_points_memcached.called, msg=(
            'Should call the get memcached Command'))
