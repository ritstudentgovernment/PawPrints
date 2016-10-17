from django.shortcuts import render, get_object_or_404, render, redirect
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import F
from datetime import datetime, timedelta
from petitions.models import Petition
from profile.models import Profile
from django.contrib.auth.models import User


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
    users_signed = Profile.objects.filter(petitions_signed=petition)

    # Generate the placeholders for the petition's page.
    # Note: 'edit' is how the system determines if the current user has the permission to edit a petition or not.
    data_object = {
        'petition': petition,
        'author':author,
        'current_user': user,
        'curr_user_signed': curr_user_signed,
        'users_signed': users_signed,
        'edit': edit_check(user, petition)
    }

    return render(request, 'petition.html', data_object)


@login_required
def petition_create(request):
    """
    Endpoint for creating a new petition.
    This requires the user be signed in.
    """

    # Build the user reference.
    user = request.user

    # Create a new blank petition.
    date = datetime.now()
    new_petition = Petition(title="New Petition", description="New Petition Description",author=user,signatures=0,created_at=date,expires=date + timedelta(days=30))
    new_petition.save()

    # Add the petition's ID to the user's created petitions list.
    petition_id = new_petition.id
    user.profile.petitions_created.add(petition_id)

    # Go to the new petition to edit its content.
    return redirect('/petition/'+str(petition_id))


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

    attribute = request.POST.get("attribute")
    value = request.POST.get("value")

    if attribute == "title":
        petition.title = value

    if attribute == "description":
        petition.description = value

    petition.save()

    return redirect('/petition/' + str(petition_id))


@login_required
@require_POST
def petition_sign(request, petition_id):
    """ Endpoint for signing a petition.
    This endpoint requires the user be signed in
    and that the HTTP request method is a POST.
    """
    petition = get_object_or_404(Petition, pk=petition_id)
    user = request.user
    user.profile.petitions_signed.add(petition)
    user.save()
    petition.update(signatures=F('signatures')+1) 
    petition.update(last_signed=datetime.utcnow())
    petition.save()
    
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
    petition.published = False    
    petition.save()

    return redirect('petition/' + str(petition_id))

# HELPER FUNCTIONS #
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
            if user.is_staff or user.id == petition.author.id:
                # The user is authenticated, and can edit the petition!
                edit = True

    return edit

# SORTING 
def most_recent():
    return Petition.objects.all() \
    .filter(expires__gt=datetime.utcnow()) \
    .exclude(has_response=True) \
    .filter(published=True) \
    .order_by('-created_at')

def most_signatures():
    return Petition.objects.all() \
    .filter(expires__gt=datetime.utcnow()) \
    .exclude(has_response=True) \
    .filter(published=True) \
    .order_by('-signatures')

def last_signed():
    return Petition.objects.all() \
    .filter(expires_gt=datetime.utcnow()) \
    .exclude(has_response=True) \
    .filter(published=True) \
    .order_by('-last_signed')
