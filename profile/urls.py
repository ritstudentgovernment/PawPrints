from django.urls import re_path
from . import views

app_name = 'profile'

urlpatterns = [
    re_path(r'^$', views.profile),
    re_path(r'^settings/notifications/staff/(?P<username>\w+)$', views.update_staff_emailing, name='staff_notification'),
    re_path(r'^settings/notifications/(?P<user_id>\d+)$', views.update_notifications, name='notification_update'),
    re_path(r'^manage/admin/alert/', views.update_alert, name='alert_update'),
    re_path(r'^manage/admin/add/(?P<user_id>\d+)$', views.add_superuser),
    re_path(r'^manage/admin/remove/(?P<user_id>\d+)$', views.remove_superuser),
    re_path(r'^manage/manager/add/(?P<user_id>\d+)$', views.add_staff_member),
    re_path(r'^manage/manager/remove/(?P<user_id>\d+)$', views.remove_staff_member),
    re_path(r'^manage/admin/', views.admin),
]
