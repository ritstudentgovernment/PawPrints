"""
Author: Peter Zujko (@zujko)
        Lukas Yelle (@lxy5611)
Description: Handles views and endpoints for all petition related operations.
Date Created: Sept 15 2016
Updated: Feb 15 2017
"""
from django.shortcuts import render, get_object_or_404, render, redirect
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from django.db.models import F, Q
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from datetime import timedelta
from petitions.models import Petition, Tag
from django.utils import timezone
from petitions.models import Petition
from profile.models import Profile
from django.contrib.auth.models import User
from channels import Group, Channel
from send_mail.tasks import *
import json


import logging

logger = logging.getLogger("pawprints."+__name__)

def index(request):
    """
    Handles displaying the index page of PawPrints.
    """
    # Get the current sorting key from the index page, if one is not set the default is 'most recent'
    sorting_key = request.POST.get('sort_by', 'most recent')

    data_object = {
        'tags': Tag.objects.all,
        'colors':colors(),
        'petitions': sorting_controller(sorting_key)
    }

    return render(request, 'index.html', data_object)


def load_petitions(request):
    """
    Handles requests for the list of petitions by AJAX.
    """
    sorting_key = request.POST.get('sort_by', 'most recent')
    filter_key = request.POST.get('filter', 'all')

    # This line gets a filtered and sorted list of petitions.
    data_object = {
        "petitions": filtering_controller(sorting_controller(sorting_key), filter_key)
    }

    return render(request, 'list_petitions.html', data_object)


def petition_responded(request):
    """
    Handles displaying all petitions with
    :param request:
    :return:
    """
    sorting_key = request.POST.get('sort_by', 'most recent')
    filter_key = request.POST.get('filter', 'all')

    data_object = {
        'tags': Tag.objects.all,
        'colors': colors(),
        "petitions": responded(filtering_controller(Petition.objects.all(), filter_key))
    }

    return render(request, 'responded.html', data_object)


def petition(request, petition_id):
    """ Handles displaying A single petition.
    DB queried to get Petition object and User objects.
    User object queries retrieve author
    and list of all users who signed the petition.
    """
    # Get petition of given id, if not found, display 404
    petition = get_object_or_404(Petition, pk=petition_id)
    # Get author of the petition
    author = User.objects.get(pk=petition.author.id)
    user = request.user

    # Check if user is authenticated before querying
    curr_user_signed = user.profile.petitions_signed.filter(id=petition.id).exists() if user.is_authenticated() else None

    # Get QuerySet of all users who signed this petition
    # Note: This returns an abstract list of IDs that are not directly associated, at least to my knowledge, to specific user objects.
    users_signed = Profile.objects.filter(petitions_signed=petition)

    # Get all of the current tags in pawprints.
    additional_tags = Tag.objects.all().exclude(name__in=[x.name for x in petition.tags.all()])


    # Generate the placeholders for the petition's page.
    # Note: 'edit' is how the system determines if the current user has the permission to edit a petition or not.
    data_object = {
        'petition': petition,
        'author':author,
        'current_user': user,
        'current_user_signed': curr_user_signed,
        'users_signed': users_signed,
        'additional_tags': additional_tags,
        'edit': edit_check(user, petition),
        'colors':colors()
    }

    return render(request, 'petition.html', data_object)


@login_required
@require_POST
def petition_create(request):
    """
    Endpoint for creating a new petition.
    This requires the user be signed in.
    Note: This endpoint returns the ID of the petition
          created, in order for JavaScript to redirect
          to the correct petition.
    """
    # Build the user reference.
    user = request.user

    # Create a new blank petition.
    date = timezone.now()
    new_petition = Petition(title="New Petition", description="New Petition Description",author=user,signatures=0,created_at=date,expires=date + timedelta(days=30))
    new_petition.save()

    # Add the petition's ID to the user's created petitions list.
    petition_id = new_petition.id
    user.profile.petitions_created.add(petition_id)

    # Auto-sign the author to the petition.
    user.profile.petitions_signed.add(new_petition)
    user.save()
    new_petition.last_signed = timezone.now()
    new_petition.signatures = F('signatures')+1
    new_petition.save()

    logger.info("user "+user.email +" created a new petion called "+new_petition.title+" ID: "+str(new_petition.id))

    # Return the petition's ID to be used to redirect the user to the new petition.
    return HttpResponse(str(petition_id))


@login_required
@require_POST
def petition_edit(request, petition_id):
    """
    Handles the updating of a particular petition.
    This endpoint requires the user be signed in
    and that the HTTP request method is a POST.
    """
    # create the petition object based on the petition id sent.
    petition = get_object_or_404(Petition, pk=petition_id)

    # Check if the user is able to edit
    if edit_check(request.user, petition):

        attribute = request.POST.get("attribute")
        value = request.POST.get("value")

        if attribute == "publish":
            user = request.user.profile
            return petition_publish(user, petition)

        if attribute == "title":
            petition.title = value

        if attribute == "description":
            petition.description = value

        if attribute == "add-tag":
            petition.tags.add(value)

        if attribute == "remove-tag":
            petition.tags.remove(value)

        petition.save()

        logger.info('user '+request.user.email+' edited petition '+petition.title+" ID: "+str(petition.id))

    return redirect('/petition/' + str(petition_id))

def get_petition(petition_id):
    """
    Handles the
    :param petition_id:
    :return:
    """
    return Petition.objects.get(pk=petition_id)


# ENDPOINTS #

@login_required
@require_POST
def petition_sign(request, petition_id):
    """ Endpoint for signing a petition.
    This endpoint requires the user be signed in
    and that the HTTP request method is a POST.
    Note: This endpoint returns the ID of the petition signed.
          This will allow AJAX to interface with the view better.
    """
    petition = get_object_or_404(Petition, pk=petition_id)
    # If the petition is still active
    if petition.status != 2:
        user = request.user
        if not user.profile.petitions_signed.filter(id=petition_id).exists():
            user.profile.petitions_signed.add(petition)
            user.save()
            petition.signatures += 1
            petition.last_signed = timezone.now()
            petition.save()

            data = {
                "command":"update-sigs",
                "sigs":petition.signatures,
                "id":petition.id
            }

            Group("petitions").send({
                "text": json.dumps(data)
            })

        logger.info('user '+request.user.email+' signed petition '+petition.title+', which now has '+str(petition.signatures)+' signatures')

	# Check if petition reached 200 if so, email.
        if petition.signatures == 200:
            petition_reached.delay(petition.id, request.META['HTTP_HOST'])
            logger.info('petition '+petition.title+' hit 200 signatures \n'+"ID: "+str(petition.id))

    return HttpResponse(str(petition.id))

@login_required
@require_POST
def petition_subscribe(request, petition_id):
    """ Endpoint subscribes a user to the petition"""
    petition = get_object_or_404(Petition, pk=petition_id)
    user = request.user
    user.profile.subscriptions.add(petition)
    user.save()

    return redirect('petition/' + str(petition_id))

@login_required
@require_POST
def petition_unsubscribe(request, petition_id):
    """ Endpoint unsubscribes a user to the petition"""
    petition = get_object_or_404(Petition, pk=petition_id)
    user = request.user
    user.profile.subscriptions.remove(petition)
    user.save()

    return redirect('petition/' + str(petition_id))

@login_required
@require_POST
@user_passes_test(lambda u: u.is_staff)
def petition_unpublish(request, petition_id):
    """ Endpoint for unpublishing a petition.
    This endpoint requires that the user be signed in,
    the HTTP request method is a POST, and that the
    user is an admin.
    """
    petition = get_object_or_404(Petition, pk=petition_id)
    # Set status to 2 to hide it from view.
    petition.status = 2
    petition.save()
    logger.info('user '+request.user.email+' unpublished petition '+petition.title)
    return HttpResponse(True)

# HELPER FUNCTIONS #
def colors():

    color_object = {
        'highlight':"#f36e21",
        'highlight_hover':'#e86920',
        'dark_text':'#0f0f0f',
        'light_text':'#f0f0f0',
        'bright_text':'#fff',
        'light_background':'#fafafa'
    }

    return color_object


def edit_check(user, petition):
    """
    Logic to determine if the user should be able to edit the petition
    Cases when this should be true:
      - User is the author of the petition
      - User is a moderator / admin
    *Note: These cases will be a setting in the future to allow the moderators to choose who
     can / cannot edit a petition
    :param user: The user object
    :param petition: The petition object
    :return: True / False, if the user can edit the current petition.
    """

    # Initially set the edit variable to false.
    edit = False
    # Check if the user is logged in
    if user.is_authenticated():
        # Check if the user's account is active (it may be disabled)
        if user.is_active:
            # Check if the user is a staff member or the author of the petition
            if user.is_staff or (user.id == petition.author.id and petition.status != 2 ):
                # The user is authenticated, and can edit the petition!
                edit = True
    return edit

def petition_publish(user, petition):
    """ Endpoint for publishing a petition.
    This endpoint requires that the user be signed in,
    the HTTP request method is a POST, the petition is new,
    and that the user is the petition's author.
    """
    response = False
    if petition.status == 0 and user.id == petition.author.id:
        # Set status to 1 to publish it to the world.
        petition.status = 1
        petition.save()
        response = True
    return HttpResponse(response)


# FILTERING
def filtering_controller(sorted_objects, tag):
    if tag == "all":
        return sorted_objects
    else:
        queried_tag = Tag.objects.get(id=tag)
        return sorted_objects.all().filter(tags=tag)


def responded(sorted_objects):
    return sorted_objects.all().filter(has_response=True)


# SORTING
#
def sorting_controller(key, query=None):
    result = {
        'most recent': most_recent(),
        'most signatures': most_signatures(),
        'last signed': last_signed(),
        'search': search(query),
	'in progress': in_progress(),
        'responded': responded()
    }.get(key, None)
    return result

def most_recent():
    return Petition.objects.all() \
    .filter(expires__gt=timezone.now()) \
    .exclude(has_response=True) \
    .filter(status=1) \
    .order_by('-created_at')

def most_signatures():
    return Petition.objects.all() \
    .filter(expires__gt=timezone.now()) \
    .exclude(has_response=True) \
    .filter(status=1) \
    .order_by('-signatures')

def last_signed():
    return Petition.objects.all() \
    .filter(expires__gt=timezone.now()) \
    .exclude(has_response=True) \
    .filter(status=1) \
    .order_by('-last_signed')

def search(query):
    vector = SearchVector('title', weight='A') + SearchVector('description', weight='A')
    query = SearchQuery(query)
    return Petition.objects.annotate(rank=SearchRank(vector, query)) \
    .select_related('author', 'response') \
    .prefetch_related('tags', 'updates') \
    .filter(status=1) \
    .filter(rank__gte=0.35) \
    .order_by('-rank')

def in_progress():
    return Petition.objects.all() \
    .filter(status=1) \
    .filter(expires__gt=timezone.now()) \
    .filter( (Q(signatures__gt=200) | ~Q(updates=None)) & Q(response=None) ) \
    .exclude(has_response=True) \
    .order_by('-created_at')

def responded():
    return Petition.objects.all() \
    .filter(status=1) \
    .filter(has_response=True) \
    .order_by('-created_at')
