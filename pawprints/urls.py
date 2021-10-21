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
from profile.views import user_logout

from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.http import HttpResponseNotFound, HttpResponseServerError
from django.template import loader
from django.template.response import TemplateResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.defaults import page_not_found, server_error

from auth.views import CompleteAuthView, InitAuthView, MetadataView
from petitions import views


def handler500(request):
    context = {'request': request}
    template_name = '500.html'
    return TemplateResponse(request, template_name, context, status=500)


urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^about/', views.about, name='about'),
    url(r'committees/', views.committees, name='committees'),
    url(r'^admin/login', InitAuthView.as_view(), name='init-auth'),
    url(r'^admin/', admin.site.urls),
    url(r'^acs$', csrf_exempt(CompleteAuthView.as_view()), name='acs'),
    url(r'^saml$', MetadataView.as_view(), name='metadata'),
    url(r'^login/', InitAuthView.as_view(), name='init-auth'),
    url(r'^logout/', user_logout, name='user_logout'),
    url(r'^petition/', include('petitions.urls')),
    url(r'^profile/', include('profile.urls')),
    url(r'^maintenance/', views.maintenance),
    url(r'^petitions/(?P<petition_id>\w+)$', views.petition_redirect)
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
