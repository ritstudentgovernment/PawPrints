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

logger = logging.getLogger("pawprints." + __name__)


@shared_task
def petition_approved(petition_id, site_path):
    petition = Petition.objects.get(pk=petition_id)

    email = EmailMessage(
        'PawPrints - Petition approved.',
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
        logger.info("Petition Approval email SEND \nPetition ID: " + str(petition.id))
    except Exception as e:
        if petition_approved.request.retries == 3:
            logger.critical("Petition Approval email FAILED \nPetition ID: " + str(petition.id), exc_info=True)
        else:
            petition_approved.retry(countdown=int(random.uniform(1, 4) ** petition_approved.request.retries), exc=e)


@shared_task
def petition_rejected(petition_id, site_path):
    petition = Petition.objects.get(pk=petition_id)

    email = EmailMessage(
        'PawPrints - Petition rejected',
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
        logger.info("Petition Rejection email SENT \nPetition ID: " + str(petition.id))
    except Exception as e:
        if petition_rejected.request.retries == 3:
            logger.critical("Petition Rejection email FAILED \nPetition ID: " + str(petition.id), exc_info=True)
        else:
            petition_rejected.retry(countdown=int(random.uniform(1, 4) ** petition_rejected.request.retries), exc=e)


@shared_task
def petition_update(petition_id, site_path):
    petition = Petition.objects.get(pk=petition_id)

    # Gets all users that are subscribed or have signed the petition and if they want to receive email updates.
    users = Profile.objects.filter(Q(subscriptions=petition) | Q(petitions_signed=petition)).filter(
        notifications__update=True).distinct("id")

    # Construct array of email addresses
    recipients = [prof.user.email for prof in users]

    email = EmailMessage(
        'PawPrints - Petition status update',
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
        recipients
    )

    email.content_subtype = "html"
    try:
        email.send()
        logger.info("Petition Update email SENT \nPetition ID: " + str(petition.id))
    except Exception as e:
        if petition_update.request.retries == 3:
            logger.critical(
                "Petition Update email FAILED \nPetition ID: " + str(petition.id) + "\nRecipients:\n" + str(recipients),
                exc_info=True)
        else:
            petition_update.retry(countdown=int(random.uniform(1, 4) ** petition_update.request.retries), exc=e)


@shared_task
def petition_responded(petition_id, site_path):
    petition = Petition.objects.get(pk=petition_id)

    # Gets all users that are subscribed or have signed the petition and if they want to receive email updates.
    users = Profile.objects.filter(Q(subscriptions=petition) | Q(petitions_signed=petition)).filter(
        notifications__response=True).distinct("id")

    # Construct array of email addresses
    recipients = [prof.user.email for prof in users]

    email = EmailMessage(
        'PawPrints - Petition response',
        get_template('email_inlined/petition_response_received.html').render(
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
        recipients
    )

    email.content_subtype = "html"
    try:
        email.send()
        logger.info("Petition Response email SENT \nPetition ID: " + str(petition.id))
    except Exception as e:
        if petition_update.request.retries == 3:
            logger.critical(
                "Petition Response email FAILED \nPetition ID: " + str(petition.id) + "\nRecipients:\n" + str(
                    recipients), exc_info=True)
        else:
            petition_update.retry(countdown=int(random.uniform(1, 4) ** petition_update.request.retries), exc=e)


@shared_task
def petition_reached(petition_id, site_path):
    petition = Petition.objects.get(pk=petition_id)

    # Gets all users that are subscribed or have signed the petition and if they want to receive emails about petition response.
    users = Profile.objects.filter(Q(subscriptions=petition) | Q(petitions_signed=petition)).filter(
        notifications__response=True).distinct("id")

    # Construct array of email addresses
    recipients = [prof.user.email for prof in users]

    email = EmailMessage(
        'PawPrints - Petition threshold reached',
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
        recipients
    )
    email.content_subtype = "html"
    try:
        email.send()
        logger.info("Petition Reached email SENT \nPetition ID: " + str(petition.id))
    except Exception as e:
        if petition_reached.request.retries == 3:
            logger.critical(
                "Petition Reached email FAILED\nPetition ID: " + str(petition.id) + "\nRecipients: " + recipients,
                exc_info=True)
        else:
            petition_reached.retry(countdown=int(random.uniform(1, 4) ** petition_reached.request.retries), exc=e)


@shared_task
def petition_received(petition_id, site_path):
    petition = Petition.objects.get(pk=petition_id)

    email = EmailMessage(
        'PawPrints - Petition received',
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

        logger.info("Petition Received email SENT \nPetition ID: " + str(petition.id))
    except Exception as e:
        if petition_received.request.retries == 3:
            logger.critical("Petition Received email FAILED \nPetition ID: " + str(petition.id), exc_info=True)
        else:
            petition_received.retry(countdown=int(random.uniform(1, 4) ** petition_received.request.retries), exc=e)


@shared_task
def petition_needs_approval(petition_id, site_path):
    petition = Petition.objects.get(pk=petition_id)

    email = EmailMessage(
        'PawPrints - Petition needs approval',
        get_template('email_inlined/petition_needs_approval.html').render(
            Context({
                'petition_id': petition.id,
                'title': petition.title,
                'author': petition.author.profile.full_name,
                'site_path': site_path,
                'protocol': 'https',
                'timestamp': time.strftime('[%H:%M:%S %d/%m/%Y]') + ' End of message'
            })
        ),
        'sgnoreply@rit.edu',
        [petition.author.email]
    )
    email.content_subtype = "html"
    try:
        email.send()
        logger.info("Petition Needs Approval email SENT \nPetition ID: " + str(petition.id))
    except Exception as e:
        if petition_needs_approval.request.retries == 3:
            logger.critical("Petition Needs Approval email FAILED \nPetition ID: " + str(petition.id))
        else:
            logger.error("Petition Needs Approval email FAILED \nPetition ID: " + str(petition.id), exc_info=True)
            petition_needs_approval.retry(countdown=int(random.uniform(1, 4) ** petition_approved.request.retries),
                                          exc=e)
