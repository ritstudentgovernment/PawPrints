from django.conf import settings
from huey.consumer import EVENT_ERROR_TASK
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Manage background tasks"

    def add_arguments(self, parser):
        parser.add_argument('-failed', dest='list_failed',
                            action='store_true', help='List failed Huey jobs')

    def handle(self, *args, **options):
        list_failed = options['list_failed']

        if list_failed:
            for event in settings.HUEY.storage:
                if event['status'] == EVENT_ERROR_TASK:
                    print(event)
