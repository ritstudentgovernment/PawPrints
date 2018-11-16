from django.conf import settings
from huey.consumer import EVENT_ERROR_TASK
from django.core.management.base import BaseCommand
import pickle
import huey
import redis
import os


class Command(BaseCommand):
    help = "Manage background tasks"
    error_key = 'huey.errors.{}'.format(settings.HUEY['name'])

    def add_arguments(self, parser):
        parser.add_argument('-failed', dest='list_failed',
                            action='store_true', help='List failed Huey jobs')

        parser.add_argument('-retry', dest='retry_failed',
                            action='store_true', help='Attempt to retry failed jobs')

    def handle(self, *args, **options):
        list_failed = options['list_failed']
        retry_failed = options['retry_failed']

        if list_failed:
            self.list_failed_tasks()
        elif retry_failed:
            self.retry_failed_tasks()

    def retry_failed_tasks(self):
        r = redis.Redis(host='redis', port=6379)

        failed = r.llen(self.error_key)

        if int(failed) == 0:
            print("No Failed jobs")

        data = r.lrange(self.error_key, 0, int(failed))
        for item in data:
            job_data = pickle.loads(item)
            if job_data['retries'] == 3:
                print("Job {} failed: {}".format(
                    job_data['task'], job_data['error']))
        yes_no = input("Attempt to retry the above jobs? [y/n]")
        if yes_no == 'y':
            # Retry jobs
            print("Retrying jobs")
        else:
            print("Operation Aborted")

    def list_failed_tasks(self):
        """
        List the jobs that have failed after their specified number of retries.
        """
        r = redis.Redis(host='redis', port=6379)

        failed = r.llen(self.error_key)

        if int(failed) == 0:
            print("No Failed jobs")

        data = r.lrange(self.error_key, 0, int(failed))
        for item in data:
            job_data = pickle.loads(item)
            if job_data['retries'] == 3:
                print("Job {} failed: {}".format(
                    job_data['task'], job_data['error']))
