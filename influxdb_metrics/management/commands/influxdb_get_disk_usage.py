"""Collects the current memory usage and sends it to influxdb."""
from django.core.management.base import BaseCommand, CommandError  # NOQA

from server_metrics.hard_disk import get_disk_usage

from ...utils import write_points


class Command(BaseCommand):
    args = '<directory>'
    help = 'Returns total disk space for the given folder.'

    def handle(self, *args, **options):
        path = '$HOME'
        if args:
            path = args[0]
        total = get_disk_usage(path)
        data = [{
            'name': 'default.server.disk.usage',
            'columns': ['value', ],
            'points': [[total, ]], }]
        print(data)
        write_points(data)
