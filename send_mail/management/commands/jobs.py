from django.conf import settings
from huey.consumer import EVENT_ERROR_TASK
from django.core.management.base import BaseCommand
from send_mail import tasks
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

        failed_tasks = []
        while(r.llen(self.error_key) != 0):
            data = r.lpop(self.error_key)
            job_data = pickle.loads(data)
            if job_data['retries'] == 3:
                print("Job {} failed: {}".format(
                    job_data['task'], job_data['error']))
                failed_tasks.append(data)

        yes_no = ""
        if len(failed_tasks) != 0:
            yes_no = input("Attempt to retry the above jobs? [y/n]: ")
        else:
            print("No Failed Jobs")
            return

        if yes_no == 'y':
            # Retry jobs
            print("Retrying jobs")
            for job_data in failed_tasks:
                job = pickle.loads(job_data)
                task_name = '_'.join(job['task'].split('_')[2:])
                arguments = job['data'][0]
                task = getattr(tasks, task_name)
                task(*arguments)  # Try the job again
        else:
            if len(failed_tasks) != 0:
                r.lpush(self.error_key, *failed_tasks)
            print("Operation Aborted")

    def list_failed_tasks(self):
        """
        List the jobs that have failed after their specified number of retries.
        """
        r = redis.Redis(host='redis', port=6379)

        failed_tasks = []
        while(r.llen(self.error_key) != 0):
            data = r.lpop(self.error_key)
            job_data = pickle.loads(data)
            if job_data['retries'] == 3:
                print("Job {} failed: {}".format(
                    job_data['task'], job_data['error']))
                failed_tasks.append(data)

        if len(failed_tasks) == 0:
            print("No Failed jobs")
        else:
            r.lpush(self.error_key, *failed_tasks)
