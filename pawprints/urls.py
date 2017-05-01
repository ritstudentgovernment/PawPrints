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
from django.conf.urls import url, include
from django.contrib import admin
from django.views.decorators.csrf import csrf_exempt
from petitions import views
from profile.views import user_login, user_logout
from auth.views import MetadataView, CompleteAuthView, InitAuthView

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^petitions/', views.load_petitions),
    url(r'^admin/', admin.site.urls),
    url(r'^saml$', MetadataView.as_view(), name='metadata'),
    url(r'^login/', InitAuthView.as_view(), name='init-auth'),
    url(r'^acs$', csrf_exempt(CompleteAuthView.as_view()), name='acs'),
    url(r'^logout/', user_logout, name='user_logout'),
    url(r'^petition/', include('petitions.urls')),
    url(r'^profile/', include('profile.urls'))
]
