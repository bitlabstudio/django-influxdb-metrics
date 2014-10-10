"""Collects the current memory usage and sends it to influxdb."""
from django.core.management.base import BaseCommand, CommandError  # NOQA

from server_metrics.postgresql import get_database_size

from ...utils import write_points


class Command(BaseCommand):
    args = '<db_role, db_name>'
    help = 'Returns total size of the given database.'

    def handle(self, *args, **options):
        db_role = None
        db_name = None
        if args:
            db_role = args[0]
            db_name = args[1]
        total = get_database_size(db_role, db_name)
        data = [{
            'name': 'default.server.postgresql.size',
            'columns': ['value', ],
            'points': [[total, ]], }]
        print(data)
        write_points(data)
