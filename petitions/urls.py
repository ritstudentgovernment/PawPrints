from django.conf.urls import url
from . import views

app_name = 'petitions'

urlpatterns = [
    url(r'^(?P<petition_id>\d+)$', views.petition),
    url(r'^create/', views.petition_create),
    url(r'^sign/(?P<petition_id>\d+)$', views.petition_sign),
    url(r'^update/(?P<petition_id>\d+)$', views.petition_edit),
    url(r'^subscribe/(?P<petition_id>\d+)$', views.petition_subscribe),
    url(r'^unsubscribe/(?P<petition_id>\d+)$', views.petition_unsubscribe),
    url(r'^unpublish/(?P<petition_id>\d+)$', views.petition_unpublish),
    url(r'^report/(?P<petition_id>\d+)$', views.petition_report, name='petition_report'),
    url(r'^bots/(?P<petition_id>\d+)$', views.petition_bots)
]
