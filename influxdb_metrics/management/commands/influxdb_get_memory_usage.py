"""Collects the current memory usage and sends it to influxdb."""
from django.core.management.base import BaseCommand, CommandError  # NOQA

from server_metrics.memory import get_memory_usage

from ...utils import write_points


class Command(BaseCommand):
    args = '<username>'
    help = 'Returns total memory of all processes of the given user.'

    def handle(self, *args, **options):
        username = None
        if args:
            username = args[0]
        total, largest_process, largest_process_name = \
            get_memory_usage(username)
        data = [{
            'name': 'default.server.memory.usage',
            'columns': ['value', 'largest_process', 'largest_process_name'],
            'points': [[total, largest_process, largest_process_name]], }]
        print(data)
        write_points(data)
