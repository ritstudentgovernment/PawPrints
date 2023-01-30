"""
Author: Peter Zujko (@zujko)
Description: Contains models for Petition, Tag, and Response.
Date Created: Sept 15 2016
Updated: Oct 17 2016
"""
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver

import bleach

bleach.sanitizer.ALLOWED_TAGS = frozenset(
    ['i', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'sub', 'br', 'sup', 'span', 'img'] +
    list(bleach.sanitizer.ALLOWED_TAGS)
)
bleach.sanitizer.ALLOWED_ATTRIBUTES['img'] = [
    'alt', 'height', 'src', 'width']
# bleach.sanitizer.ALLOWED_STYLES.extend('text-align')
for key in bleach.sanitizer.ALLOWED_ATTRIBUTES:
    bleach.sanitizer.ALLOWED_ATTRIBUTES[key].append('data-mce-style')

#
# Defines petition model.
#


class Petition(models.Model):
    title = models.CharField(max_length=80)
    description = models.TextField()
    tags = models.ManyToManyField('petitions.Tag')
    author = models.ForeignKey(User, on_delete=models.PROTECT)
    signatures = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField()
    # These states include: 0 - new (unpublished), 1 - published, 2 - removed (unpublished), 3 - Needs Review
    status = models.PositiveSmallIntegerField(default=0)
    expires = models.DateTimeField()
    last_signed = models.DateTimeField(default=None, blank=True, null=True)
    has_response = models.BooleanField(default=False)
    response = models.ForeignKey(
        'petitions.Response', default=None, blank=True, null=True, on_delete=models.SET_NULL)
    in_progress = models.BooleanField(null=True)
    updates = models.ManyToManyField('petitions.Update', default=None)
    old_id = models.CharField(
        max_length=20, default=None, blank=True, null=True)
    # Indicates to the user what committee a petition has been charged to
    # committee = models.CharField(max_length=100, default="none")

    def __str__(self):
        return str(self.title)


#
# Defines tag model.
#
class Tag(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return str(self.name)


#
# Defines a response model.
#
class Response(models.Model):
    description = models.TextField()
    created_at = models.DateTimeField()
    author = models.TextField()

    def __str__(self):
        return str(self.author)


#
# Defines an update model.
#
class Update(models.Model):
    description = models.TextField()
    created_at = models.DateTimeField()


#
# Defines the model for reporting petitions
#
class Report(models.Model):
    petition = models.ForeignKey(Petition, on_delete=models.PROTECT)
    reporter = models.ForeignKey(User, on_delete=models.PROTECT)
    reported_at = models.DateTimeField()
    reported_for = models.TextField(default='', blank=True)


#
# The following defines a signal function which is called before a save() is actually run
# on a petition object.
# The following signal function sanitizes the petition description and title.
#
@receiver(pre_save, sender=Petition)
def sanitize_petition(sender, instance, *args, **kwargs):
    del sender, args, kwargs
    instance.description = bleach.clean(instance.description)
    instance.title = bleach.clean(instance.title)
