from django.conf.urls import url
from . import views

app_name='profile'

urlpatterns = [
    url(r'^settings/notification/(?P<user_id>\d+)$', views.update_notification),
]
