"""Custom email backends for the influxdb_metrics app."""
from django.core.mail.backends.smtp import EmailBackend

from .utils import write_point


class InfluxDbEmailBackend(EmailBackend):
    """
    Custom email backend that sends the number of sent emails to InfluxDB.

    """
    def send_messages(self, email_messages):
        num_sent = super(InfluxDbEmailBackend, self).send_messages(
            email_messages)
        if num_sent:
            write_point('default.django.email.sent', 'value', num_sent)
        return num_sent
