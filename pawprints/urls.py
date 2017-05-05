"""pawprints URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.views.defaults import page_not_found, server_error
from django.template import loader
from django.http import HttpResponseServerError, HttpResponseNotFound
from django.conf.urls import url, include
from django.contrib import admin
from petitions import views
from profile.views import user_login, user_logout

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^petitions/', views.load_petitions),
    url(r'^admin/', admin.site.urls),
    url(r'^login/', user_login, name='user_login'),
    url(r'^logout/', user_logout, name='user_logout'),
    url(r'^petition/', include('petitions.urls')),
    url(r'^profile/', include('profile.urls'))
]

def handler500(request):
    t = loader.get_template('500.html')
    return HttpResponseServerError(t.render({'request': request}))

def handler404(request):
    t = loader.get_template('404.html')
    return HttpResponseNotFound(t.render())
