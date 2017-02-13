"""
Author: Omar De La Hoz (omardlhz) & Peter Zujko (zujko)
Description: Send email to pawprints users.
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

@param message Channel Message
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

def petition_update(message):
    print("Updating")
    petition = Petition.objects.get(pk=message.content.get('petition_id'))
    users = Profile.objects.filter(Q(subscriptions=petition) | Q(petitions_signed=petition)).filter(notifications__update=True).distinct("id")
    
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
