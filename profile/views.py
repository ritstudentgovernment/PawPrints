"""
Author: Peter Zujko (@zujko)
Description: Handles views and endpoints for all profile related operations.
Date Created: Nov 7 2016
Updated: Nov 8 2016
"""
from django.shortcuts import render, redirect, render
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Profile

@login_required
def profile(request):
    """ Handles displaying information about the user
    and option to update their settings.
    """
    profile = Profile.objects.get(user=request.user)
               
    return render(request, 'profile.html',{'profile': profile})

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

def login_user(request):
    """
    Endpoint that logs a user in.
    *Note: This is only a Temporary endpoint, as shibboleth SSO will be used in the future*
    """

    # Get the next page from the url
    next_url = request.GET.get("next", '')
    if not next_url:
        next_url = "/accounts/"

    logout(request)
    username = password = ''
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect(next_url)

    return render(request, 'login.html')
