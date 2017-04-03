"""
Defines background tasks that modify petitions.
Runs on celery workers.
Author: Peter Zujko
"""

from __future__ import absolute_import, unicode_literals
from celery import shared_task
from django.utils.html import strip_tags
from django.contrib.auth.models import User
from petitions.models import Petition
from .profanity import has_profanity
from send_mail.tasks import petition_approved
import bleach

@shared_task
def publish_petition_task(user_id, petition_id):
    petition = Petition.objects.get(pk=petition_id)
    user = User.objects.get(pk=user_id)
    if user.is_staff:
        petition.status = 1
        petition.body = bleach.clean(petition.body)
        petition.save()
        petition_approved.delay(petition_id, 'pawprints.rit.edu')
        # Send Message
        return
    # Check for profanities 
    body = strip_tags(petition.body) 
    if has_profanity(body):
        petition.status = 3
        petition.save()
        # Send Message
    else 
        petition.status = 1
        petition.body = bleach.clean(petition.body)
        petition.save()
        # Send Message
    
        
