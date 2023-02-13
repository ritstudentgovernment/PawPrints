from django.urls import re_path
from . import views

app_name = 'petitions'

urlpatterns = [
    re_path(r'^(?P<petition_id>\d+)$', views.petition),
    re_path(r'^create/', views.petition_create),
    re_path(r'^sign/(?P<petition_id>\d+)$', views.petition_sign),
    re_path(r'^update/(?P<petition_id>\d+)$', views.petition_edit),
    re_path(r'^subscribe/(?P<petition_id>\d+)$', views.petition_subscribe),
    re_path(r'^unsubscribe/(?P<petition_id>\d+)$', views.petition_unsubscribe),
    re_path(r'^unpublish/(?P<petition_id>\d+)$', views.petition_unpublish),
    re_path(r'^report/(?P<petition_id>\d+)$', views.petition_report, name='petition_report'),
    re_path(r'^bots/(?P<petition_id>\d+)$', views.petition_bots)
]
