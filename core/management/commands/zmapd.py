from django.core.management.base import BaseCommand, CommandError
import os
from core import zmapd
import sys


class Command(BaseCommand):
    help = 'zmapd - Zmap Manager Daemon'

    def add_arguments(self, parser):
        parser.add_argument('cmd', help="start or stop zmap manager", choices=["start", "stop", "restart", "status"])

    def handle(self, *args, **options):
        if os.geteuid() != 0:
            raise CommandError("Only root can run this command")
        cmd = options['cmd']
        if cmd == 'start':
            zmapd.start()
        elif cmd == 'stop':
            zmapd.stop()
        elif cmd == 'restart':
            zmapd.restart()
        else:
            zmapd.status()
