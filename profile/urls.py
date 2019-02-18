from django.conf.urls import url
from . import views

app_name = 'profile'

urlpatterns = [
    url(r'^$', views.profile),
    url(r'^settings/notifications/staff/(?P<username>\w+)$', views.update_staff_emailing, name='staff_notification'),
    url(r'^settings/notifications/(?P<user_id>\d+)$', views.update_notifications, name='notification_update'),
    url(r'^manage/admin/alert/', views.update_alert, name='alert_update'),
    url(r'^manage/admin/add/(?P<user_id>\d+)$', views.add_superuser),
    url(r'^manage/admin/remove/(?P<user_id>\d+)$', views.remove_superuser),
    url(r'^manage/manager/add/(?P<user_id>\d+)$', views.add_staff_member),
    url(r'^manage/manager/remove/(?P<user_id>\d+)$', views.remove_staff_member),
    url(r'^manage/admin/', views.admin),
]
