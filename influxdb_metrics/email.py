"""Custom email backends for the influxdb_metrics app."""
from django.utils import timezone

from django.core.mail.backends.smtp import EmailBackend
from django.conf import settings

from .loader import write_points


class InfluxDbEmailBackend(EmailBackend):
    """
    Custom email backend that sends the number of sent emails to InfluxDB.

    """
    def send_messages(self, email_messages):
        num_sent = super(InfluxDbEmailBackend, self).send_messages(
            email_messages)
        if num_sent:
            data = [{
                'measurement': 'django_email_sent',
                'tags': {'host': settings.INFLUXDB_TAGS_HOST, },
                'fields': {'value': num_sent, },
                'time': timezone.now().isoformat(),
            }]
            write_points(data)
        return num_sent
