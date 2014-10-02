"""Tests for the email backends of the influxdb_metrics app."""
from django.test import TestCase

from mock import patch

from ..email import InfluxDbEmailBackend


class InfluxdbDbBackendTestCase(TestCase):
    """Tests for the ``InfuxDBEmailBackend`` email backend."""
    longMessage = True

    def setUp(self):
        self.patch_write_point = patch('influxdb_metrics.email.write_point')
        self.patch_send_messages = patch(
            'django.core.mail.backends.smtp.EmailBackend.send_messages')
        self.mock_write_point = self.patch_write_point.start()
        self.mock_send_messages = self.patch_send_messages.start()
        self.mock_send_messages.return_value = 5

    def tearDown(self):
        self.patch_write_point.stop()
        self.patch_send_messages.stop()

    def test_backend(self):
        backend = InfluxDbEmailBackend()
        result = backend.send_messages([1, 2])
        self.assertEqual(result, 5, msg=(
            'Should return the number of sent emails'))
        self.assertEqual(
            self.mock_write_point.call_args[0],
            ('default.django.email.sent', 'value', 5),
            msg=('Should create a series with the correct name and column '))
