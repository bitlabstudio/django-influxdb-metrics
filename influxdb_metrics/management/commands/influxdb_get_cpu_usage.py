"""Collects the current CPU usage and sends it to influxdb."""
from django.core.management.base import BaseCommand, CommandError  # NOQA

from server_metrics.cpu import get_cpu_usage

from ...utils import write_points


class Command(BaseCommand):
    args = '<username>'
    help = 'Returns total CPU of all processes of the given user.'

    def handle(self, *args, **options):
        username = None
        if args:
            username = args[0]
        total, largest_process, largest_process_name = \
            get_cpu_usage(username)
        data = [{
            'name': 'default.server.cpu.usage',
            'columns': ['value', 'largest_process', 'largest_process_name'],
            'points': [[
                float(total), float(largest_process), largest_process_name]],
        }]
        print(data)
        write_points(data)
