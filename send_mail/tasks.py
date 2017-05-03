"""
Defines email sending tasks that will run on celery workers

Author: Peter Zujko & Omar De La Hoz

All tasks will retry at most 3 times. 
Exponential backoff with random jitter is used when retrying tasks.
"""
from __future__ import absolute_import, unicode_literals
from celery import shared_task
from petitions.models import *
from profile.models import Profile
from django.db.models import Q
from django.core.mail import EmailMessage
from django.template.loader import get_template
from django.template import Context
import time
import logging
import random

logger = logging.getLogger("pawprints."+__name__)

@shared_task
def petition_approved(petition_id, site_path):
    petition = Petition.objects.get(pk=petition_id)

    email = EmailMessage(
        'Petition approved.',
        get_template('email_inlined/petition_approved.html').render(
            {
                'petition_id': petition.id,
                'title': petition.title,
                'author': petition.author.first_name + ' ' + petition.author.last_name,
                'site_path': site_path,
                'protocol': 'https',
                'timestamp': time.strftime('[%H:%M:%S %d/%m/%Y]') + ' End of message.'
            }
        ),
        'sgnoreply@rit.edu',
        [petition.author.email],
	)

    email.content_subtype = "html"
    try:
        email.send()
        logger.info("Petition Approval email SEND \nPetition ID: "+str(petition.id))
    except Exception as e:
        if petition_approved.request.retries == 3:
            logger.critical("Petition Approval email FAILED \nPetition ID: "+str(petition.id))
        else:
            logger.error("Petition Approval email FAILED \nPetition ID: "+str(petition.id), exc_info=True)
            petition_approved.retry(countdown=int(random.uniform(1, 4) ** petition_approved.request.retries), exc=e)

@shared_task
def petition_rejected(petition_id, site_path):
    petition = Petition.objects.get(pk=petition_id)

    email = EmailMessage(
            'Petition rejected',
            get_template('email_inlined/petition_rejected.html').render(
                {
                    'petition_id': petition.id,
                    'title': petition.title,
                    'author': petition.author.profile.full_name,
                    'site_path': site_path,
                    'protocol': 'https',
                    'timestamp': time.strftime('[%H:%M:%S %d/%m/%Y]') + ' End of message'
                }
                ),
            'sgnoreply@rit.edu',
            [petition.author.email]
            )
    email.content_subtype = "html"
    try:
        email.send()
        logger.info("Petition Rejection email SENT \nPetition ID: "+str(petition.id))
    except Exception as e:
        if petition_rejected.request.retries == 3:
            logger.critical("Petition Rejection email FAILED \nPetition ID: "+str(petition.id))
        else:
            logger.error("Petition Rejection email FAILED \nPetition ID: "+str(petition.id), exc_info=True)
            petition_approved.retry(countdown=int(random.uniform(1, 4) ** petition_approved.request.retries), exc=e)
            

@shared_task
def petition_update(petition_id, site_path):
    petition = Petition.objects.get(pk=petition_id)

    # Gets all users that are subscribed or have signed the petition and if they want to receive email updates.
    users = Profile.objects.filter(Q(subscriptions=petition) | Q(petitions_signed=petition)).filter(notifications__update=True).distinct("id")

    # Construct array of email addresses
    recipients = [prof.user.email for prof in users]

    email = EmailMessage(
            'Petition status update',
            get_template('email_inlined/petition_status_update.html').render(
                    {
                        'petition_id': petition.id,
                        'title': petition.title,
                        'author': petition.author.profile.full_name,
                        'site_path': site_path,
                        'protocol': 'https',
                        'timestamp': time.strftime('[%H:%M:%S %d/%m/%Y]') + 'End of message.'
                    }
                ),
            'sgnoreply@rit.edu',
            [recipients]
            )

    email.content_subtype = "html"
    try:
        email.send()
        logger.info("Petition Update email SENT \nPetition ID: "+str(petition.id))
    except Exception as e:
        if petition_update.request.retries == 3:
            logger.critical("Petition Update email FAILED \nPetition ID: "+str(petition.id)+"\nRecipients:\n"+str(recipients))
        else:
            logger.error("Petition Update email FAILED \nPetition ID: "+str(petition.id)+"\nRecipients:\n"+str(recipients), exc_info=True)
            petition_update.retry(countdown=int(random.uniform(1,4) ** petition_update.request.retries), exc=e)


@shared_task
def petition_reached(petition_id, site_path):
    petition = Petition.objects.get(pk=petition_id)

    # Gets all users that are subscribed or have signed the petition and if they want to receive emails about petition response.
    users = Profile.objects.filter(Q(subscriptions=petition) | Q(petitions_signed=petition)).filter(notifications__response=True).distinct("id")

    # Construct array of email addresses
    recipients = [prof.user.email for prof in users]

    email = EmailMessage(
            'Petition threshold reached',
            get_template('email_inlined/petition_threshold_reached.html').render(
                    {
                        'petition_id': petition.id,
                        'title': petition.title,
                        'author': petition.author.profile.full_name,
                        'site_path': site_path,
                        'protocol': 'https',
                        'timestamp': time.strftime('[%H:%M:%S %d/%m/%Y]') + 'End of message.'
                    }
                ),
            'sgnoreply@rit.edu',
            [recipients]
            )
    email.content_subtype = "html"
    try:
        email.send()
        logger.info("Petition Reached email SENT \nPetition ID: "+str(petition.id))
    except Exception as e:
        if petition_reached.request.retries == 3:
            logger.critical("Petition Reached email FAILED\nPetition ID: "+str(petition.id)+"\nRecipients: "+recipients)
        else:
            logger.error("Petition Reached email FAILED\nPetition ID: "+str(petition.id)+"\nRecipients: "+recipients, exc_info=True)
            petition_reached.retry(countdown=int(random.uniform(1,4) ** petition_reached.request.retries), exc=e)

@shared_task
def petition_received(petition_id, site_path):
    petition = Petition.objects.get(pk=petition_id)

    email = EmailMessage(
            'Petition received',
            get_template('email_inlined/petition_rejected.html').render(
                {
                    'petition_id': petition.id,
                    'title': petition.title,
                    'author': petition.author.profile.full_name,
                    'site_path': site_path,
                    'protocol': 'https',
                    'timestamp': time.strftime('[%H:%M:%S %d/%m/%Y]') + ' End of message'
                }
                ),
            'sgnoreply@rit.edu',
            [petition.author.email]
            )
    email.content_subtype = "html"
    try:
        email.send()
        logger.info("Petition Received email SENT \nPetition ID: "+str(petition.id))
    except Exception as e:
        if petition_received.request.retries == 3:
            logger.critical("Petition Received email FAILED \nPetition ID: "+str(petition.id))
        else:
            logger.error("Petition Received email FAILED RETRYING\nPetition ID: "+str(petition.id), exc_info=True)
            petition_received.retry(countdown=int(random.uniform(1,4) ** petition_received.request.retries), exc=e)

