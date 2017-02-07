"""
Author: Omar De La Hoz (omardlhz)
Description: Send email to pawprints users.
Date Created: Nov 16 2016
Date Updated: Nov 17 2016
"""

from django.shortcuts import render
from django.shortcuts import render, get_object_or_404, render, redirect
from petitions.models import Petition
from profile.models import Profile
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.template.loader import get_template
from django.template import Context
from django.http import JsonResponse
import time


"""
Sends an email when a petition has been approved.

@param request      Request made by user.
@param recipients   The email recipients, list or comma delimited.
@param petition_id  The ID of the approved petition.

@return             {'sent': 1} if email was succesfully sent, {'sent': 0} if not.
"""
def petition_approved(message):
    try:
        petition = Petition.object.get(pk=message.content.get('petition_id'))
    except Petition.DoesNotExist:
        # Handle this error
        return

    email = EmailMessage(
        'Petition approved.',
        get_template('email_inlined/petition_approved.html').render(

            Context({
                'petition_id': message.content.get('petition_id'),
                'title': message.content.get('petition_title'),
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
    try:
        email.send()
    except:
        # log that email failed to send

"""
Send an email when a petition is rejected.

@param request      Request made by user.
@param recipients   The email recipients, list or comma delimited.
@param petition_id  The ID of the approved petition.
@param message      The reason why the  petition was rejected.

@return             {'sent': 1} if email was succesfully sent, {'sent': 0} if not.
"""
def petition_rejected(request, recipients, petition_id, message):

	petition = get_object_or_404(Petition, pk=petition_id)

	email = EmailMessage(

        'Petition rejected.',
        get_template('email_inlined/petition_rejected.html').render(

            Context({
                'petition_id': petition_id,
                'title': petition.title,
                'author': petition.author.first_name + ' ' + petition.author.last_name,
                'message': message,
                'site_path': request.META['HTTP_HOST'],
                'protocol': 'https' if request.is_secure() else 'http',
                'timestamp': time.strftime('[%H:%M:%S %d/%m/%Y]') + ' End of message.'
            })
        ),
        'sgnoreply@rit.edu',
        [recipients]
	)
	email.content_subtype = "html"
	res = email.send()

	return JsonResponse({'sent': res})


"""
Send an email when a petition is updated.

@param request      Request made by user.
@param recipients   The email recipients, list or comma delimited.
@param petition_id  The ID of the approved petition.

@return             {'sent': 1} if email was succesfully sent, {'sent': 0} if not.
"""
def petition_update(request, recipients, petition_id):

	petition = get_object_or_404(Petition, pk=petition_id)

	email = EmailMessage(

        'Petition status update.',
        get_template('email_inlined/petition_status_update.html').render(

            Context({
                'petition_id': petition_id,
                'title': petition.title,
                'author': petition.author.first_name + ' ' + petition.author.last_name,
                'site_path': request.META['HTTP_HOST'],
                'protocol': 'https' if request.is_secure() else 'http',
                'timestamp': time.strftime('[%H:%M:%S %d/%m/%Y]') + ' End of message.'
            })
        ),
        'sgnoreply@rit.edu',
        [recipients]
	)
	email.content_subtype = "html"
	res = email.send()

	return JsonResponse({'sent': res})


"""
Send an email when a petition has reached threshold.

@param request      Request made by user.
@param recipients   The email recipients, list or comma delimited.
@param petition_id  The ID of the approved petition.

@return             {'sent': 1} if email was succesfully sent, {'sent': 0} if not.
"""
def petition_reached(request, recipients, petition_id):

	petition = get_object_or_404(Petition, pk=petition_id)

	email = EmailMessage(

        'Petition treshold reached.',
        get_template('email_inlined/petition_threshold_reached.html').render(

            Context({
                'petition_id': petition_id,
                'title': petition.title,
                'author': petition.author.first_name + ' ' + petition.author.last_name,
                'site_path': request.META['HTTP_HOST'],
                'protocol': 'https' if request.is_secure() else 'http',
                'timestamp': time.strftime('[%H:%M:%S %d/%m/%Y]') + ' End of message.'
            })
        ),
        'sgnoreply@rit.edu',
        [recipients]
	)
	email.content_subtype = "html"
	res = email.send()

	return JsonResponse({'sent': res})


"""
Send an email when a petition is reported.

@param request      Request made by user.
@param recipients   The email recipients, list or comma delimited.
@param petition_id  The ID of the approved petition.
@param reason       Reason why the petition was reported.

@return             {'sent': 1} if email was succesfully sent, {'sent': 0} if not.
"""
def petition_report(request, recipients, petition_id, reason):

	petition = get_object_or_404(Petition, pk=petition_id)

	email = EmailMessage(

        'Petition reported.',
        get_template('email_inlined/report_petition.html').render(

            Context({
                'petition_id': petition_id,
                'title': petition.title,
                'author': petition.author.first_name + ' ' + petition.author.last_name,
                'reason': reason,
                'site_path': request.META['HTTP_HOST'],
                'protocol': 'https' if request.is_secure() else 'http',
                'timestamp': time.strftime('[%H:%M:%S %d/%m/%Y]') + ' End of message.'
            })
        ),
        'sgnoreply@rit.edu',
        [recipients]
	)
	email.content_subtype = "html"
	res = email.send()

	return JsonResponse({'sent': res})


"""
Send an email when a petition is received.

@param request      Request made by user.
@param recipients   The email recipients, list or comma delimited.
@param petition_id  The ID of the approved petition.

@return             {'sent': 1} if email was succesfully sent, {'sent': 0} if not.
"""
def petition_received(request, recipients, petition_id):

	petition = get_object_or_404(Petition, pk=petition_id)

	email = EmailMessage(

        'Petition response received.',
        get_template('email_inlined/petition_response_received.html').render(

            Context({
                'petition_id': petition_id,
                'title': petition.title,
                'author': petition.author.first_name + ' ' + petition.author.last_name,
                'site_path': request.META['HTTP_HOST'],
                'protocol': 'https' if request.is_secure() else 'http',
                'timestamp': time.strftime('[%H:%M:%S %d/%m/%Y]') + ' End of message.'
            })
        ),
        'sgnoreply@rit.edu',
        [recipients]
	)
	email.content_subtype = "html"
	res = email.send()

	return JsonResponse({'sent': res})
