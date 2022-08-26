from django.core.management import BaseCommand
from django_redis import get_redis_connection

from core.models import User

# This command is creating in our cache a key called rankings which contains all the rankings of the ambassadors
# However, it has to be manually called when appropriate to update the cache.
class Command(BaseCommand):
    def handle(self, *args, **option):
        con = get_redis_connection("default")
        ambassadors = User.objects.filter(is_ambassador=True)

        for ambassador in ambassadors:
           con.zadd('rankings', {ambassador.name: float(ambassador.revenue)})
