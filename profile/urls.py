from django.conf.urls import url
from . import views

app_name='profile'

urlpatterns = [
    url(r'^$', views.profile),
    url(r'^settings/notifications/(?P<user_id>\d+)$', views.update_notifications, name='notification_update'),
]
