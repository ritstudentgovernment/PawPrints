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

bleach.sanitizer.ALLOWED_TAGS.extend([u'i',u'h1', u'h2',u'h3', u'h4', u'h5', u'h6',u'p',u'sub',u'br',u'sup', u'span',u'img'])
bleach.sanitizer.ALLOWED_ATTRIBUTES[u'img'] = [u'alt', u'height', u'src', u'width']
bleach.sanitizer.ALLOWED_STYLES.extend(u'text-align')
for key in bleach.sanitizer.ALLOWED_ATTRIBUTES.keys():
    bleach.sanitizer.ALLOWED_ATTRIBUTES[key].append(u'data-mce-style')


#
# Defines petition model.
#
class Petition(models.Model):
    read_only = ['has_response', 'response']
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
    response = models.ForeignKey('petitions.Response', default=None, blank=True, null=True, on_delete=models.SET_NULL)
    in_progress = models.NullBooleanField()
    updates = models.ManyToManyField('petitions.Update', default=None)
    old_id = models.CharField(max_length=20, default=None, blank=True, null=True)
    #committee = models.CharField(max_length=100, default=None)

    def __str__(self):
        return self.title


#
# Defines tag model.
#
class Tag(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


#
# Defines a response model.
#
class Response(models.Model):
    description = models.TextField()
    created_at = models.DateTimeField()
    author = models.TextField()

    def __str__(self):
        return self.author


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
    instance.description = bleach.clean(instance.description)
    instance.title = bleach.clean(instance.title)
