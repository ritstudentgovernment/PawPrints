"""
Defines Celery settings.
"""

from __future__ import absolute_import, unicode_literals
import os
import raven
from raven.contrib.celery import register_signal, register_logger_signal
import django
from pawprints import secrets
from celery import Celery


class Celery(Celery):
    def on_configure(self):
        client = raven.Client(secrets.RAVEN_DSN)

        # Register filter to filter out duplicate logs
        register_logger_signal(client)

        # Hook into Celery error handling
        register_signal(client)


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pawprints.settings')
django.setup()

app = Celery('pawprints')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
