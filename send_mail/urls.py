from django.conf.urls import url
from . import views

app_name='send_mail'

urlpatterns = [
	url(r'^approved/(?P<petition_id>\d+)/(?P<recipients>[\w.%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4})/', views.petition_approved),
	url(r'^rejected/(?P<petition_id>\d+)/(?P<recipients>[\w.%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4})/(?P<message>[\w\-]+)/$', views.petition_rejected),
	url(r'^updated/(?P<petition_id>\d+)/(?P<recipients>[\w.%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4})/', views.petition_update),
	url(r'^reached/(?P<petition_id>\d+)/(?P<recipients>[\w.%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4})/', views.petition_reached),
	url(r'^report/(?P<petition_id>\d+)/(?P<recipients>[\w.%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4})/(?P<reason>[\w\-]+)/$', views.petition_report),
	url(r'^received/(?P<petition_id>\d+)/(?P<recipients>[\w.%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4})/', views.petition_received),
]