from django.shortcuts import render, get_object_or_404, render
from petitions.models import Petition
from profile.models import Profile

def petition(request, petition_id):
    petition = get_object_or_404(Petition, pk=petition_id) 
    author = Profile.objects.get(petitions_created=petition)
    user = request.user
    users_signed = Profile.objects.filter(petitions_signed=petition)

    data_object = {
        'petition': petition,
        'current_user': user,
        'users_signed': users_signed
    }

    return render(request, '', data_object)      
