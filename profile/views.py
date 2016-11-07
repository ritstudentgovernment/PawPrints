from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

# ENDPOINTS #
@login_required
@require_POST
def update_notification(request, user_id):
    if request.user.id != int(user_id):
        return redirect('/')

    user = request.user
    setting = request.POST.get('notification','')
    value = request.POST.get('value','')

    if setting == 'update': 
        user.profile.notifications.update = True if value == '1' else False 
    elif setting == 'response':
        user.profile.notifications.update = True if value == '1' else False
    user.save()
    return redirect('profile/settings/'+str(user_id)) 
