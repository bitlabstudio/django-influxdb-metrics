"""Tests for the ``influxdb_get_postgresql_size`` management command."""
from django.test import TestCase

from mock import patch

from ..management.commands.influxdb_get_postgresql_size import Command


class InfluxdbGetPostgresqlSizeTestCase(TestCase):
    """Tests for the ``influxdb_get_postgresql_size`` management command."""
    longMessage = True

    def setUp(self):
        self.patch_write_points = patch(
            'influxdb_metrics.management.commands.influxdb_get_postgresql_size'
            '.write_points')
        self.patch_get_database_size = patch(
            'influxdb_metrics.management.commands.influxdb_get_postgresql_size'
            '.get_database_size')
        self.mock_write_points = self.patch_write_points.start()
        self.mock_get_database_size = self.patch_get_database_size.start()

    def tearDown(self):
        self.patch_get_database_size.stop()
        self.patch_write_points.stop()

    def test_command(self):
        cmd = Command()
        cmd.handle('db_role', 'db_user')
        write_points_call_args = self.mock_write_points.call_args[0][0]
        get_database_size_call_args = \
            self.mock_get_database_size.call_args[0]

        self.assertEqual(
            write_points_call_args[0]['measurement'],
            'postgresql_size', msg=(
                'Should construct a data dict with the correct columns'))
        self.assertEqual(
            get_database_size_call_args,
            ('db_role', 'db_user'),
            msg=('Should call `get_database_size` with correct parameters'))
