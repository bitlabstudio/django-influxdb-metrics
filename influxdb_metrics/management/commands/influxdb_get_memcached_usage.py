"""Collects memcached usage stats and sends it to influxdb."""
from django.core.management.base import BaseCommand, CommandError  # NOQA

from server_metrics.memcached import get_memcached_usage

from ...utils import write_points


class Command(BaseCommand):
    args = '<socket path>'
    help = 'Returns memcached usage stats.'

    def handle(self, *args, **options):
        socket = None
        if args:
            socket = args[0]
        bytes_, curr_items = get_memcached_usage(socket)
        data = [{
            'name': 'default.server.memcached.usage',
            'columns': ['value', 'curr_items', ],
            'points': [[bytes_, curr_items, ]],
        }]
        print(data)
        write_points(data)
