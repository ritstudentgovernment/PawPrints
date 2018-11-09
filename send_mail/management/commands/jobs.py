from django.conf import settings
from huey.consumer import EVENT_ERROR_TASK
from django.core.management.base import BaseCommand
import huey
import redis
import os


class Command(BaseCommand):
    help = "Manage background tasks"
    error_key = 'huey.errors.{}'.format('edisueynstance')

    def add_arguments(self, parser):
        parser.add_argument('-failed', dest='list_failed',
                            action='store_true', help='List failed Huey jobs')

    def handle(self, *args, **options):
        list_failed = options['list_failed']

        if list_failed:
            self.list_failed_tasks()

    def list_failed_tasks(self):
        """
        List the jobs that have failed after their specified number of retries.
        """"
        r = redis.Redis(host='redis', port=6379)

        failed = r.llen(self.error_key)

        if int(failed) == 0:
            print("No Failed jobs")

        data = r.lrange(self.error_key, 0, int(failed))
        for item in data:
            print(item.decode('ascii'))
