"""Collects the current memory usage and sends it to influxdb."""
from django.conf import settings
from django.utils import timezone
from django.core.management.base import BaseCommand, CommandError  # NOQA

from server_metrics.postgresql import get_database_size

from ...loader import write_points


class Command(BaseCommand):
    args = '<db_role, db_name>'
    help = 'Returns total size of the given database.'

    def handle(self, *args, **options):
        db_role = None
        db_name = None
        if args:
            db_role = args[0]
            db_name = args[1]
        use_localhost = getattr(
            settings, 'INFLUXDB_POSTGRESQL_USE_LOCALHOST', False)
        total = get_database_size(db_role, db_name, localhost=use_localhost)
        data = [{
            'measurement': 'postgresql_size',
            'tags': {'host': settings.INFLUXDB_TAGS_HOST, },
            'fields': {'value': total, },
            'time': timezone.now().isoformat(),
        }]
        print(data)
        write_points(data)
