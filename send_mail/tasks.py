"""
Defines email sending tasks that will run in the background with Huey

Author: Peter Zujko & Omar De La Hoz & Lukas Yelle (lxy5611)

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
    Petition_Reported = email_titles['reported']
    Petition_Charged = email_titles['charged']


def generate_email(petition_id, event, site_path, to=None, bcc=None, email_data=None):
    petition = Petition.objects.get(pk=petition_id)

    if event in email_titles:
        to = petition.author.email if to is None else to

        if email_data is None:
            email_data = {
                'petition_id': petition.id,
                'title': petition.title,
                'first_name': petition.author.first_name,
                'author': petition.author.profile.full_name,
                'site_path': site_path,
                'protocol': 'https',
                'timestamp': time.strftime('[%H:%M:%S %d/%m/%Y]') + ' End of message.',
                'organization': ORGANIZATION,
                'email_header': COLORS['email_header'],
                'org_logo': ORG_LOGO,
                'name': NAME,
                'header_image': HEADER_IMAGE
            }
        email = EmailMessage(
            email_titles[event],
            get_template('email_inlined/petition_' + event + '.html').render(email_data),
            EMAIL_ADDR,
            [to],
            bcc=bcc,
        )
        email.content_subtype = "html"
        return email
    return None


def send_email(email, petition_id, event):
    try:
        email.send()
        logger.info(
            "Petition " + event + " email SEND \nPetition ID: " + str(petition_id))
    except Exception as e:
        logger.critical(
            "Petition " + event + " email FAILED \nPetition ID: " + str(petition_id), exc_info=True)
        raise e


@db_task(retries=3, retry_delay=3)
def petition_approved(petition_id, site_path):
    email = generate_email(petition_id, 'approved', site_path)
    send_email(email, petition_id, 'Approved')


@db_task(retries=3, retry_delay=3)
def petition_rejected(petition_id, site_path):
    email = generate_email(petition_id, 'rejected', site_path)
    send_email(email, petition_id, 'Rejected')


@db_task(retries=3, retry_delay=3)
def petition_update(petition_id, site_path):
    petition = Petition.objects.get(pk=petition_id)

    # Gets all users that are subscribed or have signed the petition and if they want to receive email updates.
    users = Profile.objects.filter(Q(subscriptions=petition) | Q(petitions_signed=petition)).filter(
        notifications__update=True).distinct("id")

    # Construct array of email addresses
    recipients = [prof.user.email for prof in users]

    email = generate_email(petition_id, 'updated', site_path, EMAIL_ADDR, recipients)
    send_email(email, petition_id, 'Status Update')


@db_task(retries=3, retry_delay=3)
def petition_responded(petition_id, site_path):
    petition = Petition.objects.get(pk=petition_id)

    # Gets all users that are subscribed or have signed the petition and if they want to receive email updates.
    users = Profile.objects.filter(Q(subscriptions=petition) | Q(petitions_signed=petition)).filter(
        notifications__response=True).distinct("id")

    # Construct array of email addresses
    recipients = [prof.user.email for prof in users]

    email = generate_email(petition_id, 'responded', site_path, EMAIL_ADDR, recipients)
    send_email(email, petition_id, 'Response Received')


@db_task(retries=3, retry_delay=3)
def petition_reached(petition_id, site_path):
    petition = Petition.objects.get(pk=petition_id)

    # Gets all users that are subscribed or have signed the petition and if they want to receive emails about petition response.
    users = Profile.objects.filter(
        Q(subscriptions=petition) |
        Q(petitions_signed=petition) |
        Q(notifications__threshold=True)
    ).filter(notifications__response=True).distinct("id")

    # Construct array of email addresses
    recipients = [prof.user.email for prof in users]

    email = generate_email(petition_id, 'reached', site_path, EMAIL_ADDR, recipients)
    send_email(email, petition_id, 'Threshold Reached')


@db_task(retries=3, retry_delay=3)
def petition_received(petition_id, site_path):
    email = generate_email(petition_id, 'received', site_path)
    send_email(email, petition_id, 'Received')


@db_task(retries=3, retry_delay=3)
def petition_needs_approval(petition_id, site_path):
    email = generate_email(petition_id, 'needs_approval', site_path)
    send_email(email, petition_id, 'Needs Approval')


@db_task(retries=3, retry_delay=3)
def petition_reported(petition_id, report_id, site_path):
    petition = Petition.objects.get(pk=petition_id)
    report = Report.objects.get(pk=report_id)
    reporter = User.objects.get(pk=report.reporter_id)

    # Gets all users that are on the email list for reported petitions.
    users = Profile.objects.filter(notifications__reported=True).distinct("id")

    # Construct array of email addresses
    recipients = [prof.user.email for prof in users]

    email_data = {
                    'petition_id': petition.id,
                    'title': petition.title,
                    'first_name': petition.author.first_name,
                    'author': petition.author.profile.full_name,
                    'reason': report.reported_for,
                    'reporter': reporter.profile.display_name,
                    'site_path': site_path,
                    'protocol': 'https',
                    'timestamp': time.strftime('[%H:%M:%S %d/%m/%Y]') + ' End of message',
                    'organization': ORGANIZATION,
                    'email_header': COLORS['email_header'],
                    'org_logo': ORG_LOGO,
                    'name': NAME,
                    'header_image': HEADER_IMAGE
                 }
    email = generate_email(petition_id, 'reported', site_path, EMAIL_ADDR, recipients, email_data)
    send_email(email, petition_id, 'Reported')
