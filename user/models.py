from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Extends User model. Defines sn and notifications for a User.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    sn = models.CharField(max_length=60)
    notifications = models.ForeignKey(Notifications, on_delete=models.CASCADE)

# Defines user's email notification settings.
class Notifications(models.Model):
    update = models.BooleanField(default=True)
    response = models.BooleanField(default=True) 

# 
# The following functions define signals so that the Profile model 
# will be automatically created/updated whenever the Django User object 
# is created/updated. This makes it so you never have to call the Profile
# object's save method, all saving is done with the User model.
#
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
