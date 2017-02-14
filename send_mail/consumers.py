"""
Author: Omar De La Hoz (omardlhz) & Peter Zujko (zujko)
Description: Send email to pawprints users.

Date Update: Feb 13 2017

This runs on a worker. Messages are formatted as

{
    "petition_id": <id>,
    "site_path": "<site_path>"
}

and formatted as the following for a rejection.

{
    "petition_id": <id>,
    "site_path": "<site_path>",
    "message": "<message>"
}
"""

from petitions.models import Petition
from channels.generic.websockets import WebsocketConsumer
from profile.models import Profile
from django.db.models import Q
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.template.loader import get_template
from django.template import Context
from django.http import JsonResponse
import time


"""
Sends an email when a petition has been approved.
"""
def petition_approved(message):
    try:
        petition = Petition.objects.get(pk=message.content.get('petition_id'))
    except Petition.DoesNotExist:
        # Handle this error
        return

    email = EmailMessage(
        'Petition approved.',
        get_template('email_inlined/petition_approved.html').render(
            Context({
                'petition_id': petition.id,
                'title': petition.title,
                'author': petition.author.first_name + ' ' + petition.author.last_name,
                'site_path': message.content.get('site_path'),
                'protocol': 'https',
                'timestamp': time.strftime('[%H:%M:%S %d/%m/%Y]') + ' End of message.'
            })
        ),
        'sgnoreply@rit.edu',
        [petition.author.email]
	)

    email.content_subtype = "html"
    email.send()

"""
Sends email when a petition is rejected.
"""
def petition_rejected(message):
    petition = Petition.objects.get(pk=message.content.get('petition_id'))

    email = EmailMessage(
            'Petition rejected',
            get_template('email_inlined/petition_rejected.html').render(
                Context({
                    'petition_id': petition.id,
                    'title': petition.title,
                    'author': petition.author.profile.full_name,
                    'message': message.content.get('message'),
                    'site_path': message.content.get('site_path'),
                    'protocol': 'https',
                    'timestamp': time.strftime('[%H:%M:%S %d/%m/%Y]') + ' End of message'
                    })
                ),
            'sgnoreply@rit.edu',
            [petition.author.email]
            )
    email.content_subtype = "html"
    email.send()

"""
Sends email when a petition is updated.
"""
def petition_update(message):
    petition = Petition.objects.get(pk=message.content.get('petition_id'))

    # Gets all users that are subscribed or have signed the petition and if they want to receive email updates.
    users = Profile.objects.filter(Q(subscriptions=petition) | Q(petitions_signed=petition)).filter(notifications__update=True).distinct("id")
    
    # Construct array of email addresses
    recipients = [prof.user.email for prof in users]

    email = EmailMessage(
            'Petition status update',
            get_template('email_inlined/petition_status_update.html').render(
                    Context({
                        'petition_id': petition.id,
                        'title': petition.title,
                        'author': petition.author.profile.full_name,
                        'site_path': message.content.get('site_path'),
                        'protocol': 'https',
                        'timestamp': time.strftime('[%H:%M:%S %d/%m/%Y]') + 'End of message.'
                        })
                ),
            'sgnoreply@rit.edu',
            [recipients]
            )
    
    email.content_subtype = "html"
    email.send()

"""
Sends email once a petition reaches 200 signatures.
"""
def petition_reached(message):
    petition = Petition.objects.get(pk=message.content.get("petition_id"))

    # Gets all users that are subscribed or have signed the petition and if they want to receive emails about petition response.
    users = Profile.objects.filter(Q(subscriptions=petition) | Q(petitions_signed=petition)).filter(notifications__response=True).distinct("id")
    
    # Construct array of email addresses
    recipients = [prof.user.email for prof in users]

    email = EmailMessage(
            'Petition threshold reached',
            get_template('email_inlined/petition_threshold_reached.html').render(
                    Context({
                        'petition_id': petition.id,
                        'title': petition.title,
                        'author': petition.author.profile.full_name,
                        'site_path': message.content.get('site_path'),
                        'protocol': 'https',
                        'timestamp': time.strftime('[%H:%M:%S %d/%m/%Y]') + 'End of message.'
                        })
                ),
            'sgnoreply@rit.edu',
            [recipients]
            )
    email.content_subtype = "html"
    email.send()
