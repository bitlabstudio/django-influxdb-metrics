"""Tests for the ``influxdb_get_cpu_memory_usage`` management command."""
from django.test import TestCase

from mock import patch

from ..management.commands.influxdb_get_cpu_memory_usage import Command


class InfluxdbGetCPUMemoryUsageTestCase(TestCase):
    """Tests for the ``influxdb_get_cpu_memory_usage`` management command."""
    longMessage = True

    def setUp(self):
        super(InfluxdbGetCPUMemoryUsageTestCase, self).setUp()
        self.patch_write_points_cpu = patch(
            'influxdb_metrics.management.commands.influxdb_get_cpu_usage.'
            'write_points')
        self.patch_write_points_memory = patch(
            'influxdb_metrics.management.commands.influxdb_get_memory_usage.'
            'write_points')
        self.mock_write_points_cpu = self.patch_write_points_cpu.start()
        self.mock_write_points_memory = self.patch_write_points_memory.start()

    def tearDown(self):
        super(InfluxdbGetCPUMemoryUsageTestCase, self).tearDown()
        self.patch_write_points_cpu.stop()
        self.patch_write_points_memory.stop()

    def test_command(self):
        cmd = Command()
        cmd.handle('foo', 'bar')
        self.assertTrue(self.mock_write_points_cpu.called, msg=(
            'Should call the get cpu Command'))
        self.assertTrue(self.mock_write_points_memory.called, msg=(
            'Should call the get memory Command'))
