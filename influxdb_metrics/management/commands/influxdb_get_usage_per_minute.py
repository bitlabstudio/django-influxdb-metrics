"""
Collects CPU, memory and memcached usage and sends it to influxdb.

This just calls ``influxdb_get_cpu_usage``, ``influxdb_get_memory_usage`` and
``influxdb_get_memcached_usage``.

This is helpful because you will want both commands to be scheduled every
minute which means crontab will start both processes at the same time and CPU
usage will always be near 100% because the CPU command will measure the CPU
usage of the memory command.

"""
from django.core.management.base import BaseCommand, CommandError  # NOQA

from .influxdb_get_cpu_usage import Command as CPUCommand
from .influxdb_get_memory_usage import Command as MemoryCommand
from .influxdb_get_memcached_usage import Command as MemcachedCommand


class Command(BaseCommand):
    args = '<username_cpu> <username_memory> <memcached socket>'
    help = 'Returns CPU, memory and memcached usage.'

    def handle(self, *args, **options):
        username_cpu = None
        username_memory = None
        memcached_socket = None
        if len(args) >= 1:
            username_cpu = args[0]
        if len(args) >= 2:
            username_memory = args[1]
        if len(args) >= 3:
            memcached_socket = args[2]

        cpu_command = CPUCommand()
        cpu_command.handle(username_cpu)
        memory_command = MemoryCommand()
        memory_command.handle(username_memory)
        memcached_command = MemcachedCommand()
        memcached_command.handle(memcached_socket)
