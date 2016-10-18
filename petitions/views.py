from django.shortcuts import render, get_object_or_404, render, redirect
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import F
from datetime import datetime
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
    curr_user_signed = user.profile.partner_set.filter(petitions_signed=petition).exists() if user.is_authenticated() else None

    # Get QuerySet of all users who signed this petition
    users_signed = Profile.objects.filter(petitions_signed=petition)
    
    data_object = {
        'petition': petition,
        'current_user': user,
        'curr_user_signed': curr_user_signed,
        'users_signed': users_signed,
        'curr_user_petition': author == user
    }

    return render(request, 'petition.html', data_object)      

# ENDPOINTS #

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
    petition.signatures += 1
    petition.last_signed = datetime.utcnow()
    petition.save()
    
    return redirect('/petition/'+str(petition_id))

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

@login_required
@require_POST
@user_passes_test(lambda u: u.is_staff)
def add_tag(request):
    tag_name = request.POST.get('name', '')
    if tag_name != '':
        tag = Tag(name=tag_name)
        tag.save()

    return redirect(request.META.get('HTTP_REFERER'))

# HELPER FUNCTIONS #

# PETITION SORTING 
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
            .filter(expires__gt=datetime.utcnow()) \
            .exclude(has_response=True) \
            .filter(published=True) \
            .order_by('-last_signed')

def all_active():
    """All petitions that have no yet expired"""
    return Petition.objects.all() \
            .filter(expires__gt=datetime.utcnow()) \
            .exclude(published=False) \
            .order_by('-created_at')

def all_inactive():
    """All petitions that have expired and are published"""
    return Petition.objects.all() \
            .filter(expires__lt=datetime.utcnow()) \
            .exclude(published=False) \
            .order_by('-created_at')
