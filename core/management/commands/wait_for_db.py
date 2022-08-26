from django.core.management import BaseCommand
from django.db import connections
from django.db.utils import OperationalError

import time


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write('Attempting to connect do database')
        conn = None

        while not conn:
            try:
                conn = connections['default']
                time.sleep(5)
            except OperationalError:
                self.stdout.write('Database unavailable - attempting to connect again in 1 second...')
                time.sleep(5)

            self.stdout.write(self.style.SUCCESS('Database is available!'))