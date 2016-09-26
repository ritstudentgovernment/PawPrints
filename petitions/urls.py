from django.conf.urls import url
from . import views

app_name='petitions'

urlpatterns = [
    url(r'^(?P<petition_id>\d+)$', views.petition),
    url(r'^sign/(?P<petition_id>\d+)$', views.petition_sign)
]
