from django.conf.urls import url
from . import views

app_name='petitions'

urlpatterns = [
    url(r'^(?P<petition_id>\d+)$', views.petition),
    url(r'^sign/(?P<petition_id>\d+)$', views.petition_sign),
    url(r'^unpublish/(?P<petition_id>\d+)$', views.petition_unpublish),
    url(r'^email/(?P<petition_id>\d+)/(?P<emailType>\w+)/(?P<recipients>[\w.%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4})/', views.sendEmail),
    url(r'^htmlemail/(?P<recipients>[\w.%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4})/', views.sendSimpleEmail)
]
