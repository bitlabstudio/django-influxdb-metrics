"""Tests for the loader module of the influxdb_metrics app."""
from django.test import TestCase

from .. import loader


class LoaderMeasurementPrefixTestCase(TestCase):
    """Tests for the ``INFLUXDB_PREFIX`` setting."""
    longMessage = True

    def test_default_prefix(self):
        self.assertEqual(
            loader.measurement_name_for('request'),
            'django_request'
        )

    def test_custom_prefix(self):
        with self.settings(INFLUXDB_PREFIX='test'):
            self.assertEqual(
                loader.measurement_name_for('metric'),
                'test_metric'
            )

    def test_empty_prefix(self):
        with self.settings(INFLUXDB_PREFIX=''):
            self.assertEqual(
                loader.measurement_name_for('thing1'),
                'thing1'
            )

        with self.settings(INFLUXDB_PREFIX=None):
            self.assertEqual(
                loader.measurement_name_for('thing2'),
                'thing2'
            )
