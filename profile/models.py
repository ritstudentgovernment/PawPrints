"""
models.py
Peter Zujko (pxz3370)
Lukas Yelle (lxy5611)
10/20/16
Update: Nov 18 2016
"""
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


# Extends User model. Defines sn and notifications for a User.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.TextField()
    notifications = models.ForeignKey('profile.Notifications', on_delete=models.CASCADE)
    subscriptions = models.ManyToManyField('petitions.Petition', related_name='profile_subscriptions', blank=True)
    petitions_created = models.ManyToManyField('petitions.Petition', related_name='profile_petitions_created', blank=True)
    petitions_signed = models.ManyToManyField('petitions.Petition', related_name='profile_petitions_signed', blank=True)
    display_name = models.CharField(max_length=3, blank=True)
    # 0 - Does not have access, 1 - Has Access
    has_access = models.PositiveSmallIntegerField(default=1)

    def __unicode__(self):
        return self.user.username


# Defines user's email notification settings.
class Notifications(models.Model):
    update = models.BooleanField(default=True)
    response = models.BooleanField(default=True)
    reported = models.BooleanField(default=False)
    threshold = models.BooleanField(default=False)


# Defines the model for an app-wide, after login, popup on user clients
class GlobalAlert(models.Model):
    active = models.BooleanField(default=True)
    content = models.TextField()


# 
# The following functions define signals so that the Profile model 
# will be automatically created/updated whenever the Django User object 
# is created/updated. This makes it so you never have to call the Profile
# object's save method, all saving is done with the User model.
#
@receiver(post_save, sender=User)
def create_user_profile(_, instance, created, **__):
    if created:
        Profile.objects.create(user=instance, notifications=Notifications.objects.create())


@receiver(post_save, sender=User)
def save_user_profile(_, instance, **__):
    instance.profile.save()
    instance.profile.notifications.save()
