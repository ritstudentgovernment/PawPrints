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

from django.urls import re_path
from django.conf import settings
from django.conf.urls import include
from django.conf.urls.static import static
from django.contrib import admin
from django.template.response import TemplateResponse
from django.views.decorators.csrf import csrf_exempt

from auth.views import CompleteAuthView, InitAuthView, MetadataView
from petitions import views


def handler500(request):
    context = {'request': request}
    template_name = '500.html'
    return TemplateResponse(request, template_name, context, status=500)


urlpatterns = [
    re_path(r'^$', views.index, name='index'),
    re_path(r'^about/', views.about, name='about'),
    re_path(r'committees/', views.committees, name='committees'),
    re_path(r'^news/', views.news, name='news'),
    re_path(r'^admin/login', InitAuthView.as_view(), name='init-auth'),
    re_path(r'^admin/', admin.site.urls),
    re_path(r'^acs$', csrf_exempt(CompleteAuthView.as_view()), name='acs'),
    re_path(r'^saml$', MetadataView.as_view(), name='metadata'),
    re_path(r'^login/', InitAuthView.as_view(), name='init-auth'),
    re_path(r'^logout/', user_logout, name='user_logout'),
    re_path(r'^petition/', include('petitions.urls')),
    re_path(r'^profile/', include('profile.urls')),
    re_path(r'^maintenance/', views.maintenance),
    re_path(r'^petitions/(?P<petition_id>\w+)$', views.petition_redirect)
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
