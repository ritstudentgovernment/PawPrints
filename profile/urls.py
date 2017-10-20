from django.conf.urls import url
from . import views

app_name='profile'

urlpatterns = [
    url(r'^$', views.profile),
    url(r'^settings/notifications/(?P<user_id>\d+)$', views.update_notifications, name='notification_update'),
    url(r'^manage/staff',views.manage_staff),
    url(r'^manage/staff/add_superuser/(?P<user_id>\d+)$',views.add_superuser, name='add_superuser'),
    url(r'^manage/staff/add_staff_member/(?P<user_id>\d+)$',views.add_staff_member, name='add_staff_member')
]
