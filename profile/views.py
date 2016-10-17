from django.shortcuts import render, get_object_or_404, render, redirect
from django.http import *
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout

@login_required
def main(request):
    """
    Redirects the user to whatever page they came from if they are logged in.
    """

    # Get the next page from the url
    next_url = request.GET.get("next",'')
    if not next_url:
        next_url = "/"

    return redirect(next_url)


def login_user(request):
    """
    Endpoint that logs a user in.
    *Note: This is only a Temporary endpoint, as shibboleth SSO will be used in the future*
    """

    # Get the next page from the url
    next_url = request.GET.get("next",'')
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