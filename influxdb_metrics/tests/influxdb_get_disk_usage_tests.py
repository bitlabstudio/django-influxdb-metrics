"""Tests for the ``influxdb_get_disk_usage`` management command."""
from django.test import TestCase

from mock import patch

from ..management.commands.influxdb_get_disk_usage import Command


class InfluxdbGetDiskUsageTestCase(TestCase):
    """Tests for the ``influxdb_get_disk_usage`` management command."""
    longMessage = True

    def setUp(self):
        self.patch_write_points = patch(
            'influxdb_metrics.management.commands.influxdb_get_disk_usage'
            '.write_points')
        self.patch_get_disk_usage = patch(
            'influxdb_metrics.management.commands.influxdb_get_disk_usage'
            '.get_disk_usage')
        self.mock_write_points = self.patch_write_points.start()
        self.mock_get_disk_usage = self.patch_get_disk_usage.start()

    def tearDown(self):
        self.patch_get_disk_usage.stop()
        self.patch_write_points.stop()

    def test_command(self):
        cmd = Command()
        cmd.handle()
        write_points_call_args = self.mock_write_points.call_args[0][0]
        get_disk_usage_call_args = self.mock_get_disk_usage.call_args[0][0]
        self.assertEqual(
            write_points_call_args[0]['columns'],
            ['value', ],
            msg=('Should construct a data dict with the correct columns'))
        self.assertEqual(
            '$HOME',
            get_disk_usage_call_args,
            msg=('Should set folder to `$HOME` as a default'))

        cmd.handle('/opt/influxdb/')
        get_disk_usage_call_args = self.mock_get_disk_usage.call_args[0][0]
        self.assertEqual(
            '/opt/influxdb/',
            get_disk_usage_call_args,
            msg=('Should get the size of the given folder'))
