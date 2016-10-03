from django.shortcuts import render, get_object_or_404, render, redirect
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.db.models import F
from datetime import datetime
from petitions.models import Petition
from profile.models import Profile

def petition(request, petition_id):
    petition = get_object_or_404(Petition, pk=petition_id) 
    author = Profile.objects.get(petitions_created=petition)
    user = request.user
    curr_user_signed = user.partner_set.filter(petitions_signed=petition).exists()
    users_signed = Profile.objects.filter(petitions_signed=petition)
    
    data_object = {
        'petition': petition,
        'current_user': user,
        'curr_user_signed': curr_user_signed,
        'users_signed': users_signed
    }

    return render(request, '', data_object)      

@login_required
@require_POST
def petition_sign(request, petition_id):
    petition = get_object_or_404(Petition, pk=petition_id)
    user = request.user
    user.profile.petitions_signed.add(petition)
    user.save()
    petition.update(signatures=F('signatures')+1) 
    petition.update(last_signed=datetime.now())
    petition.save()
    
    return redirect('petition/' + str(petition_id))

# HELPER FUNCTIONS #

# SORTING 
def most_recent():
    return Petition.objects.all() \
    .filter(expires__gt=datetime.now()) \
    .exclude(has_response=True) \
    .filter(published=True) \
    .order_by('-created_at')

def most_signatures():
    return Petition.objects.all() \
    .filter(expires__gt=datetime.now()) \
    .exclude(has_response=True) \
    .filter(published=True) \
    .order_by('-signatures')

def last_signed():
    return Petition.objects.all() \
    .filter(expires_gt=datetime.now()) \
    .exclude(has_response=True) \
    .filter(published=True) \
    .order_by('-last_signed')
