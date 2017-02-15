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
