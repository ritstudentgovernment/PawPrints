"""
Author: Peter Zujko (@zujko)
        Lukas Yelle (@lxy5611)
Description: Handles views and endpoints for all petition related operations.
Date Created: Sept 15 2016
Updated: Oct 03 2017
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse, JsonResponse
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
import petitions.profanity
import json
from collections import namedtuple

import logging

logger = logging.getLogger("pawprints." + __name__)

# PETITION DEFAULT CONSTANTS.
PETITION_DEFAULT_TITLE = "Action-oriented, one-line statement"
PETITION_DEFAULT_BODY = "Explanation and reasoning behind your petition. Why should someone sign? How will it improve the community?"


def index(request):
    """
    Handles displaying the index page of PawPrints.
    """
    # Get the current sorting key from the index page, if one is not set the default is 'most recent'
    sorting_key = request.POST.get('sort_by', 'most recent')

    data_object = {
        'tags': Tag.objects.all,
        'colors': colors()
    }

    return render(request, 'index.html', data_object)


def about(request):
    """
    Handles displaying the about page
    """
    data_object = {
        'colors': colors(),
    }

    return render(request, 'about.html', data_object)


def maintenance(request):
    return render(request, 'Something_Special.html')


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
    curr_user_signed = user.profile.petitions_signed.filter(
        id=petition.id).exists() if user.is_authenticated else None

    # Get QuerySet of all users who signed this petition
    users_signed = Profile.objects.filter(petitions_signed=petition)

    # Get all of the current tags in pawprints.
    additional_tags = Tag.objects.all().exclude(name__in=[x.name for x in petition.tags.all()])

    # Generate the placeholders for the petition's page.
    # Note: 'edit' is how the system determines if the current user has the permission to edit a petition or not.
    data_object = {
        'petition': petition,
        'author': author,
        'current_user': user,
        'current_user_signed': curr_user_signed,
        'users_signed': users_signed,
        'additional_tags': additional_tags,
        'edit': edit_check(user, petition),
        'colors': colors(),
        'default_title': PETITION_DEFAULT_TITLE,
        'default_body': PETITION_DEFAULT_BODY
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

    new_user_petitions = user.profile.petitions_created.filter(Q(status=0))
    if new_user_petitions.count() > 0:
        return HttpResponse(new_user_petitions.first().id)

    last_petition = Petition.objects.all().last()

    # Create a new blank petition.
    date = timezone.now()
    new_petition = Petition(
        title=PETITION_DEFAULT_TITLE,
        description=PETITION_DEFAULT_BODY,
        author=user,
        signatures=0,
        created_at=date,
        expires=date + timedelta(days=30),
        in_progress=False,
        id=last_petition.id + 1 if last_petition is not None else 0
    )
    new_petition.save()

    # Add the petition's ID to the user's created petitions list.
    petition_id = new_petition.id
    user.profile.petitions_created.add(petition_id)

    # Auto-sign the author to the petition.
    user.profile.petitions_signed.add(new_petition)
    user.save()
    new_petition.last_signed = timezone.now()
    new_petition.signatures = F('signatures') + 1
    new_petition.save()

    logger.info(
        "user " + user.email + " created a new petition called " + new_petition.title + " ID: " + str(new_petition.id))

    # Return the petition's ID to be used to redirect the user to the new petition.
    return HttpResponse(str(petition_id))


def petition_redirect(request, petition_id):
    """
    Handles the redirection of petitions from the old URL format to the new format.
    :param request: The user request.
    :param petition_id: The id of the petition to redirect to.
    :return: redirect to correct page.
    """

    try:

        # Check if the petition_id sent is not an integer
        int(petition_id)
        return redirect("/?p=" + str(petition_id))

    except ValueError:

        # Check if any petition in the database has the old_id that was sent.
        petition = Petition.objects.filter(old_id=petition_id)
        if petition.exists():

            # We found the petition with that old_id, redirect to it.
            return redirect("/?p=" + str(petition.first().id))

        # The petition id sent was neither an integer or in the database as an old_id, redirect home.
        return redirect("/")


@require_POST
# @login_required
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

            # Be sure the person cannot publish a petition that contains profanity.
            if petitions.profanity.has_profanity(value):
                return JsonResponse({
                    "Error": "Petitions may not contain profanity. Please correct this and try again."
                })

            if petition.title == PETITION_DEFAULT_TITLE:
                return JsonResponse({
                    "Error": "Oops! Looks like you forgot to change the title of the petition."
                })

            if petition.description == PETITION_DEFAULT_BODY:
                return JsonResponse({
                    "Error": "Oops! Looks like you forgot to change the body of the petition."
                })

            if petition.tags.count() == 0:
                return JsonResponse({
                    "Error": "Oops! Looks like you forgot to add a tag to your petition."
                })

            data = {
                "command": "new-petition",
                "petition": {
                    "petition_id": petition_id
                }
            }

            send_update(data)

            user = request.user
            return petition_publish(user, petition)

        elif attribute == "title":

            if petitions.profanity.has_profanity(value):
                return JsonResponse({
                    "Error": "Petitions may not contain profanity. Please correct this and try again."
                })

            # Update the petition title
            petition.title = value

            # Update petition created and expires dates.
            date = timezone.now()
            petition.created_at = date
            petition.expires = date + timedelta(days=30)

        elif attribute == "description":

            if petitions.profanity.has_profanity(value):
                return JsonResponse({
                    "Error": "Petitions may not contain profanity. Please correct this and try again."
                })

            # Update the petition description
            petition.description = value

            # Update petition created and expires dates.
            date = timezone.now()
            petition.created_at = date
            petition.expires = date + timedelta(days=30)

        elif attribute == "add-tag":

            petition.tags.add(value)

        elif attribute == "remove-tag":

            petition.tags.remove(value)

        elif request.user.is_staff:

            # STAFF ONLY OPERATIONS

            if attribute == "add_update":

                update = Update(
                    description=value,
                    created_at=timezone.now()
                )
                update.save()

                petition.updates.add(update)

                # Send update command over websocket.
                data = {
                    "command": "new-update",
                    "update": {
                        "description": value,
                        "timestamp": timezone.now().strftime("%B %d, %Y"),
                        "petition_id": petition_id
                    }
                }
                send_update(data)

                # Send email regarding updates.
                petition_update(petition.id, request.META['HTTP_HOST'])

            elif attribute == "response":

                last_response = Response.objects.all().last()
                last_response_id = last_response.id if last_response is not None else 0

                response = Response(
                    description=value,
                    created_at=timezone.now(),
                    author=request.user.profile.full_name,
                    id=last_response_id+1
                )
                response.save()

                petition.response = response
                petition.has_response = True
                petition.in_progress = False

                # Send response command over websocket
                data = {
                    "command": "new-response",
                    "response": {
                        "description": value,
                        "timestamp": timezone.now().strftime("%B %d, %Y"),
                        "author": request.user.profile.full_name,
                        "petition_id": petition_id
                    }
                }
                send_update(data)

                # Send email regarding the response.
                petition_responded(petition_id, request.META['HTTP_HOST'])

            elif attribute == "mark-in-progress":

                petition.in_progress = True

                data = {
                    "command": "mark-in-progress",
                    "petition": {
                        "petition_id": petition_id
                    }
                }
                send_update(data)

            elif attribute == "unpublish":

                petition.status = 2

                # Send unpublish command over websocket
                data = {
                    "command": "remove-petition",
                    "petition": {
                        "petition_id": petition_id
                    }
                }
                send_update(data)

                # Notify author that the petition was rejected over email.
                petition_rejected(petition_id, request.META['HTTP_HOST'])

            elif attribute == "editUpdate":

                new_value = json2obj(value)
                position = int(new_value.position)
                updates = petition.updates.all()
                for index, update in enumerate(updates):
                    if index == position:
                        update.description = new_value.update
                        update.save()

                return JsonResponse({"EditUpdate": "Done."})

            else:
                return JsonResponse({"Error": "Operation " + attribute + " Not Known."})

        else:
            return JsonResponse({"Error": "Operation " + attribute + " Not Known."})

    else:
        # User was unable to perform any edit operation on this petition.
        return JsonResponse({"Error": "Operation Not Permitted."})

    petition.save()

    logger.info('user ' + request.user.email + ' edited petition ' + petition.title + " ID: " + str(petition.id))

    return JsonResponse({"petition": petition_id})


def get_petition(petition_id, user):
    """
    Handles grabbing one petition
    :param: petition_id: The id of the petition to grab
            user: The logged in user object from request.user
    :return: A petition object or False
    """

    profile = user.profile if hasattr(user, "profile") else False

    petition = Petition.objects.filter(pk=petition_id)
    if petition.exists():
        petition = petition.first()
        if (petition.status != 0 and petition.status != 2) or (
                profile and profile.user.username == petition.author.username):
            return petition
    return False


# ENDPOINTS #

@login_required
@require_POST
def petition_sign(request, petition_id):
    """
    Endpoint for signing a petition.
    This endpoint requires the user be signed in
    and that the HTTP request method is a POST.
    Note: This endpoint returns the ID of the petition signed.
          This will allow AJAX to interface with the view better.
    """
    user = request.user
    petition = get_object_or_404(Petition, pk=petition_id)
    # If the user has access to pawprints and the petition is both published and still active
    if user.profile.has_access == 1 and petition.status != 0 and petition.status != 2:
        if not user.profile.petitions_signed.filter(id=petition_id).exists():
            user.profile.petitions_signed.add(petition)
            user.save()
            petition.signatures += 1
            petition.last_signed = timezone.now()
            petition.save()

            data = {
                "command": "update-sigs",
                "sigs": petition.signatures,
                "petition_id": petition.id
            }

            send_update(data)

        logger.info('user ' + request.user.email + ' signed petition ' + petition.title + ', which now has ' + str(
            petition.signatures) + ' signatures')

        # Check if petition reached 200 if so, email.
        if petition.signatures == 200:
            petition_reached(petition.id, request.META['HTTP_HOST'])
            logger.info('petition ' + petition.title + ' hit 200 signatures \n' + "ID: " + str(petition.id))

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


def petition_publish(user, petition):
    """ Endpoint for publishing a petition.
    This endpoint requires that the user be signed in,
    the petition is new, and that the user is the
    petition's author.
    """
    response = False
    # If the user has access to pawprints.
    if user.profile.has_access == 1:
        # If the petition has not previously been published, and the user is the petition's author.
        if petition.status == 0 and user.id == petition.author.id:
            # Set status to 1 to publish it to the world.
            petition.status = 1
            # Resets the created_at date to be sure the petition is active for as long as it is supposed to be.
            date = timezone.now()
            petition.created_at = date
            petition.expires = date + timedelta(days=30)
            # Save the petition.
            petition.save()
            response = True

            data = {
                "new-petition": petition.id
            }

            send_update(data)

    return HttpResponse(response)


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
    logger.info('user ' + request.user.email + ' unpublished petition ' + petition.title)
    return HttpResponse(True)


# HELPER FUNCTIONS #
def send_update(update):
    """
    Sends an update to the channels group petitions via websocket
    :param update: object
    :return: None
    """
    Group("petitions").send({
        "text": json.dumps(update)
    })
    return None


def colors():
    color_object = {
        'highlight': "#f36e21",
        'highlight_hover': '#e86920',
        'dark_text': '#0f0f0f',
        'light_text': '#f0f0f0',
        'bright_text': '#fff',
        'light_background': '#fafafa'
    }

    return color_object


def _json_object_hook(d): return namedtuple('X', d.keys())(*d.values())


def json2obj(data): return json.loads(data, object_hook=_json_object_hook)


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
    if user.is_authenticated:
        # Check if the user's account is active (it may be disabled)
        if user.is_active:
            # Check if the user is a staff member or the author of the petition.
            # If it is the petition's author, the petition must not have already been published.
            if user.is_staff or (user.id == petition.author.id and petition.status == 0):
                # The user is authenticated, and can edit the petition!
                edit = True
    return edit


# FILTERING
def filtering_controller(sorted_objects, tag):
    if tag == "all":
        return sorted_objects
    else:
        return sorted_objects.all().filter(tags=tag)


# SORTING
def sorting_controller(key, query=None):
    result = {
        'most recent': most_recent(),
        'most signatures': most_signatures(),
        'last signed': last_signed(),
        'search': search(query),
        'in progress': in_progress(),
        'responded': responded(),
        'archived': archived(),
        'similar': similar_petitions(query)
    }.get(key, None)
    return result


def most_recent():
    return Petition.objects.all() \
        .filter(expires__gt=timezone.now()) \
        .filter(status=1) \
        .order_by('-created_at')


def most_signatures():
    return Petition.objects.all() \
        .filter(expires__gt=timezone.now()) \
        .filter(status=1) \
        .order_by('-signatures')


def last_signed():
    return Petition.objects.all() \
        .filter(expires__gt=timezone.now()) \
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


def similar_petitions(query):
    vector = SearchVector('title', weight='A') + SearchVector('description', weight='A')
    query = SearchQuery(query)
    return Petition.objects.annotate(rank=SearchRank(vector, query)) \
        .filter(rank__gte=0.3) \
        .filter(status=1) \
        .order_by('-rank')


def in_progress():
    return Petition.objects.all() \
        .filter(status=1) \
        .filter(in_progress=True) \
        .exclude(has_response=True) \
        .order_by('-created_at')


def responded():
    return Petition.objects.all() \
        .filter(has_response=True) \
        .filter(status=1) \
        .order_by('-created_at')


def archived():
    return Petition.objects.all() \
        .filter(expires__lt=timezone.now()) \
        .filter(Q(response=None)) \
        .filter(status=1) \
        .order_by('-created_at')
