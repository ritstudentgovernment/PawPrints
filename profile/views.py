"""
Author: Peter Zujko (@zujko)
Description: Handles views and endpoints for all profile related operations.
Date Created: Nov 7 2016
Updated: Dec 5 2016
"""
from django.shortcuts import render, redirect, render
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, logout
from django.contrib.auth import login as auth_login
from .models import Profile
import logging

logger = logging.getLogger("pawprints."+__name__)

@login_required
def profile(request):
    """ Handles displaying information about the user
    and option to update their settings.
    """
    profile = Profile.objects.get(user=request.user)
    data_object = {
        'first_name': profile.user.first_name,
        'last_name': profile.user.last_name,
        'petitions_created': profile.petitions_created.all
    }

    return render(request, 'profile.html', data_object)

def user_login(request):
    """ Handles rendering login page and POST
    endpoint for logging in a user
    """
    return render(request, 'login.html')

# ENDPOINTS #
@login_required
@require_POST
def update_notifications(request, user_id):
    """ Handles updating a users
    notification settings.
    """
    if request.user.id != int(user_id):
        return redirect('/')

    user = request.user

    user.profile.notifications.update = True if "updates" in request.POST else False
    user.profile.notifications.response = True if "response" in request.POST else False

    user.save()
    return redirect('profile/settings/'+str(user_id))

@login_required
@require_POST
def user_logout(request):
    """ Handles logging a user out
    """
    logout(request)
    url_next = request.GET.get('next','/')
    return redirect(url_next)
