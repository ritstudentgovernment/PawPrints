"""
Author: Peter Zujko (@zujko)
Description: Handles views and endpoints for all profile related operations.
Date Created: Nov 7 2016
Updated: Dec 5 2016
"""
from django.shortcuts import render, redirect, render
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, logout
from django.contrib.auth import login as auth_login
from django.http import HttpResponse, JsonResponse
from petitions.views import colors
from .models import Profile
import logging
from django.db.models import Q

logger = logging.getLogger("pawprints." + __name__)


@login_required
def profile(request):
    """ Handles displaying information about the user
    and option to update their settings.
    """
    profile = Profile.objects.get(user=request.user)
    data_object = {
        'first_name': profile.user.first_name,
        'last_name': profile.user.last_name,
        'email': profile.user.email,
        'uid': profile.user.id,
        'notification_settings': profile.notifications,
        'petitions_created': profile.petitions_created.filter(~Q(status=2)),
        "colors": colors()
    }
    return render(request, 'profile.html', data_object)


@login_required
@user_passes_test(lambda u: u.is_superuser)
def manage_staff(request):
    """
    Handles displaying the staff managing panel.
    User must be logged in and a superuser.
    """
    profile = Profile.objects.get(user=request.user)
    superusers = User.objects.filter(is_superuser=True)
    superusers_id = superusers.values("id")
    data_object = {
        'superusers': superusers,
        'staff': User.objects.filter(is_staff=True).exclude(id__in=superusers_id),
        'all_users': User.objects.all(),
        "colors": colors()
    }
    return render(request, 'staff_manage.html', data_object)


def user_login(request):
    """ Handles rendering login page and POST
    endpoint for logging in a user
    """
    url_next = request.GET.get('next', '/profile/')
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            user_obj = User.objects.get(username=user.username)
            user_obj.is_active = True
            user_obj.backend = 'django.contrib.auth.backends.ModelBackend'
            user_obj.save()
            auth_login(request, user_obj)
            logger.info(user.username + " logged in")
            return redirect(url_next)
    data_object = {
        "colors": colors()
    }
    return render(request, 'login.html', data_object)


# ENDPOINTS #
@require_POST
@login_required
def add_superuser(request, user_id):
    if request.user.is_superuser:
        if user_id is not None:
            user = User.objects.get(id=int(user_id))
            user.is_superuser = True
            user.is_staff = True
            user.save()
            return HttpResponse(True)
    return HttpResponseForbidden(False)


@require_POST
@login_required
def add_staff_member(request, user_id):
    if request.user.is_superuser:
        if user_id is not None:
            user = User.objects.get(id=int(user_id))
            user.is_staff = True
            user.save()
            return HttpResponse(True)
    return HttpResponseForbidden(False)


@require_POST
@login_required
def remove_superuser(request, user_id):
    if request.user.is_superuser:
        if user_id is not None:
            user = User.objects.get(id=int(user_id))
            user.is_superuser = False
            user.save()
            return HttpResponse(True)
    return HttpResponseForbidden(False)


@require_POST
@login_required
def remove_staff_member(request, user_id):
    if request.user.is_superuser:
        if user_id is not None:
            user = User.objects.get(id=int(user_id))
            user.is_staff = False
            user.save()
            return HttpResponse(True)
    return HttpResponseForbidden(False)


@login_required
@require_POST
def update_notifications(request, user_id):
    """ Handles updating a users
    notification settings.
    """
    if request.user.id != int(user_id):
        return HttpResponse(False)

    user = request.user

    user.profile.notifications.update = True if "updates" in request.POST else False
    user.profile.notifications.response = True if "response" in request.POST else False

    user.save()
    return HttpResponse(True)


@login_required
def user_logout(request):
    """ Handles logging a user out
    """
    logout(request)
    url_next = request.GET.get('next', '/')
    return redirect(url_next)
