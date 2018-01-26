"""
Defines background tasks that modify petitions.
Runs on huey workers.
Author: Peter Zujko
"""

from django.utils.html import strip_tags
from django.utils import timezone
from django.contrib.auth.models import User
from petitions.models import Petition
from huey.contrib.djhuey import db_task
from .profanity import has_profanity
from send_mail.tasks import petition_approved, petition_needs_approval
import bleach

@db_task(retries=2, retry_delay=1)
def publish_petition_task(user_id, petition_id, site_path):
    petition = Petition.objects.get(pk=petition_id)
    user = User.objects.get(pk=user_id)
    if user.is_staff:
        petition.status = 1
        petition.body = bleach.clean(petition.body)
        time = timezone.now()
        expire_time = time + timedelta(days=30)
        petition.created_at = time
        petition.expires = expire_time
        petition.save()
        petition_approved(petition_id, site_path)
        # Send Message
        return
    # Check for profanities
    body = strip_tags(petition.body)
    if has_profanity(body):
        petition.status = 3
        petition.save()
        petition_needs_approval(petition_id, site_path)
        # Send Message
    else:
        petition.status = 1
        petition.body = bleach.clean(petition.body)
        petition.save()
        petition_approved(petition_id, site_path)
        # Send Message
