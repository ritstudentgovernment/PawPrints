from django.conf.urls import url
from . import views

app_name='profile'

urlpatterns = [
    url(r'^$', views.profile),
    url(r'^settings/notifications/(?P<user_id>\d+)$', views.update_notifications, name='notification_update'),
    url(r'^manage/staff',views.manage_staff),
    url(r'^manage/staff/superuser/add/(?P<user_id>\d+)$',views.add_superuser),
    url(r'^manage/staff/superuser/remove/(?P<user_id>\d+)$',views.remove_superuser),
    url(r'^manage/staff/staff_member/add/(?P<user_id>\d+)$',views.add_staff_member),
    url(r'^manage/staff/staff_member/remove/(?P<user_id>\d+)$',views.remove_staff_member)
]
