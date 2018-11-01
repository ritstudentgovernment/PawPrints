"""
Defines email sending tasks that will run in the background with Huey

Author: Peter Zujko & Omar De La Hoz

All db_tasks will retry at most 3 times.
"""
from petitions.models import *
from profile.models import Profile
from django.conf import settings
from django.db.models import Q
from django.core.mail import EmailMessage
from django.template.loader import get_template
from django.template import Context
from huey.contrib.djhuey import db_task
import time
import logging

logger = logging.getLogger("pawprints." + __name__)

email_titles = settings.CONFIG['email']
EMAIL_ADDR = settings.EMAIL_EMAIL_ADDR
ORGANIZATION = settings.CONFIG['organization']
COLORS = settings.CONFIG['email']['colors']
ORG_LOGO = settings.CONFIG['org_logo']
NAME = settings.CONFIG['name']
HEADER_IMAGE = settings.CONFIG['email']['header_image']


class EmailTitles():
    Petition_Approved = email_titles['approved']
    Petition_Rejected = email_titles['rejected']
    Petition_Update = email_titles['updated']
    Petition_Responded = email_titles['responded']
    Petition_Reached = email_titles['reached']
    Petition_Needs_Approval = email_titles['needs_approval']
    Petition_Received = email_titles['received']


@db_task(retries=3, retry_delay=3)
def petition_approved(petition_id, site_path):
    petition = Petition.objects.get(pk=petition_id)

    email = EmailMessage(
        EmailTitles.Petition_Approved,
        get_template('email_inlined/petition_approved.html').render(
            {
                'petition_id': petition.id,
                'title': petition.title,
                'first_name': petition.author.first_name,
                'author': petition.author.first_name + ' ' + petition.author.last_name,
                'site_path': site_path,
                'protocol': 'https',
                'timestamp': time.strftime('[%H:%M:%S %d/%m/%Y]') + ' End of message.',
                'organization': ORGANIZATION,
                'email_header': COLORS['email_header'],
                'org_logo': ORG_LOGO,
                'name': NAME,
                'header_image': HEADER_IMAGE
            }
        ),
        EMAIL_ADDR,
        [petition.author.email],
    )

    email.content_subtype = "html"
    try:
        email.send()
        logger.info(
            "Petition Approval email SEND \nPetition ID: " + str(petition.id))
    except Exception as e:
        logger.critical(
            "Petition Approval email FAILED \nPetition ID: " + str(petition.id), exc_info=True)
        raise e


@db_task(retries=3, retry_delay=3)
def petition_rejected(petition_id, site_path):
    petition = Petition.objects.get(pk=petition_id)

    email = EmailMessage(
        EmailTitles.Petition_Rejected,
        get_template('email_inlined/petition_rejected.html').render(
            {
                'petition_id': petition.id,
                'title': petition.title,
                'first_name': petition.author.first_name,
                'author': petition.author.profile.full_name,
                'site_path': site_path,
                'protocol': 'https',
                'timestamp': time.strftime('[%H:%M:%S %d/%m/%Y]') + ' End of message',
                'organization': ORGANIZATION,
                'email_header': COLORS['email_header'],
                'org_logo': ORG_LOGO,
                'name': NAME,
                'header_image': HEADER_IMAGE
            }
        ),
        EMAIL_ADDR,
        [petition.author.email]
    )
    email.content_subtype = "html"
    try:
        email.send()
        logger.info(
            "Petition Rejection email SENT \nPetition ID: " + str(petition.id))
    except Exception as e:
        logger.critical(
            "Petition Rejection email FAILED \nPetition ID: " + str(petition.id), exc_info=True)
        raise e


@db_task(retries=3, retry_delay=3)
def petition_update(petition_id, site_path):
    petition = Petition.objects.get(pk=petition_id)

    # Gets all users that are subscribed or have signed the petition and if they want to receive email updates.
    users = Profile.objects.filter(Q(subscriptions=petition) | Q(petitions_signed=petition)).filter(
        notifications__update=True).distinct("id")

    # Construct array of email addresses
    recipients = [prof.user.email for prof in users]

    email = EmailMessage(
        EmailTitles.Petition_Update,
        get_template('email_inlined/petition_status_update.html').render(
            {
                'petition_id': petition.id,
                'title': petition.title,
                'author': petition.author.profile.full_name,
                'site_path': site_path,
                'protocol': 'https',
                'timestamp': time.strftime('[%H:%M:%S %d/%m/%Y]') + 'End of message.',
                'organization': ORGANIZATION,
                'email_header': COLORS['email_header'],
                'org_logo': ORG_LOGO,
                'name': NAME,
                'header_image': HEADER_IMAGE
            }
        ),
        EMAIL_ADDR,
        [EMAIL_ADDR],
        bcc=recipients
    )

    email.content_subtype = "html"
    try:
        email.send()
        logger.info(
            "Petition Update email SENT \nPetition ID: " + str(petition.id))
    except Exception as e:
        logger.critical("Petition Update email FAILED \nPetition ID: " + str(petition.id) + "\nRecipients:\n" + str(recipients),
                        exc_info=True)
        raise e


@db_task(retries=3, retry_delay=3)
def petition_responded(petition_id, site_path):
    petition = Petition.objects.get(pk=petition_id)

    # Gets all users that are subscribed or have signed the petition and if they want to receive email updates.
    users = Profile.objects.filter(Q(subscriptions=petition) | Q(petitions_signed=petition)).filter(
        notifications__response=True).distinct("id")

    # Construct array of email addresses
    recipients = [prof.user.email for prof in users]

    email = EmailMessage(
        EmailTitles.Petition_Responded,
        get_template('email_inlined/petition_response_received.html').render(
            {
                'petition_id': petition.id,
                'title': petition.title,
                'author': petition.author.profile.full_name,
                'site_path': site_path,
                'protocol': 'https',
                'timestamp': time.strftime('[%H:%M:%S %d/%m/%Y]') + 'End of message.',
                'organization': ORGANIZATION,
                'email_header': COLORS['email_header'],
                'org_logo': ORG_LOGO,
                'name': NAME,
                'header_image': HEADER_IMAGE
            }
        ),
        EMAIL_ADDR,
        [EMAIL_ADDR],
        bcc=recipients
    )

    email.content_subtype = "html"
    try:
        email.send()
        logger.info(
            "Petition Response email SENT \nPetition ID: " + str(petition.id))
    except Exception as e:
        logger.critical(
            "Petition Response email FAILED \nPetition ID: " + str(petition.id) + "\nRecipients:\n" + str(recipients), exc_info=True)
        raise e


@db_task(retries=3, retry_delay=3)
def petition_reached(petition_id, site_path):
    petition = Petition.objects.get(pk=petition_id)

    # Gets all users that are subscribed or have signed the petition and if they want to receive emails about petition response.
    users = Profile.objects.filter(Q(subscriptions=petition) | Q(petitions_signed=petition)).filter(
        notifications__response=True).distinct("id")

    # Construct array of email addresses
    recipients = [prof.user.email for prof in users]

    email = EmailMessage(
        EmailTitles.Petition_Reached,
        get_template('email_inlined/petition_threshold_reached.html').render(
            {
                'petition_id': petition.id,
                'title': petition.title,
                'author': petition.author.profile.full_name,
                'site_path': site_path,
                'protocol': 'https',
                'timestamp': time.strftime('[%H:%M:%S %d/%m/%Y]') + 'End of message.',
                'organization': ORGANIZATION,
                'email_header': COLORS['email_header'],
                'org_logo': ORG_LOGO,
                'name': NAME,
                'header_image': HEADER_IMAGE
            }
        ),
        EMAIL_ADDR,
        [EMAIL_ADDR],
        bcc=recipients
    )
    email.content_subtype = "html"
    try:
        email.send()
        logger.info(
            "Petition Reached email SENT \nPetition ID: " + str(petition.id))
    except Exception as e:
        logger.critical("Petition Reached email FAILED\nPetition ID: " +
                        str(petition.id) + "\nRecipients: " + str(recipients), exc_info=True)
        raise e


@db_task(retries=3, retry_delay=3)
def petition_received(petition_id, site_path):
    petition = Petition.objects.get(pk=petition_id)

    email = EmailMessage(
        EmailTitles.Petition_Received,
        get_template('email_inlined/petition_rejected.html').render(
            {
                'petition_id': petition.id,
                'title': petition.title,
                'author': petition.author.profile.full_name,
                'site_path': site_path,
                'protocol': 'https',
                'timestamp': time.strftime('[%H:%M:%S %d/%m/%Y]') + ' End of message',
                'organization': ORGANIZATION,
                'email_header': COLORS['email_header'],
                'org_logo': ORG_LOGO,
                'name': NAME,
                'header_image': HEADER_IMAGE
            }
        ),
        EMAIL_ADDR,
        [petition.author.email]
    )
    email.content_subtype = "html"
    try:
        email.send()
        logger.info(
            "Petition Received email SENT \nPetition ID: " + str(petition.id))
    except Exception as e:
        logger.critical(
            "Petition Received email FAILED \nPetition ID: " + str(petition.id), exc_info=True)
        raise e


@db_task(retries=3, retry_delay=3)
def petition_needs_approval(petition_id, site_path):
    petition = Petition.objects.get(pk=petition_id)

    email = EmailMessage(
        EmailTitles.Petition_Needs_Approval,
        get_template('email_inlined/petition_needs_approval.html').render(
            {
                'petition_id': petition.id,
                'title': petition.title,
                'author': petition.author.profile.full_name,
                'site_path': site_path,
                'protocol': 'https',
                'timestamp': time.strftime('[%H:%M:%S %d/%m/%Y]') + ' End of message',
                'organization': ORGANIZATION,
                'email_header': COLORS['email_header'],
                'org_logo': ORG_LOGO,
                'name': NAME,
                'header_image': HEADER_IMAGE
            }
        ),
        EMAIL_ADDR,
        [petition.author.email]
    )
    email.content_subtype = "html"
    try:
        email.send()
        logger.info(
            "Petition Needs Approval email SENT \nPetition ID: " + str(petition.id))
    except Exception as e:
        logger.critical(
            "Petition Needs Approval email FAILED \nPetition ID: " + str(petition.id), exc_info=True)
        raise e
