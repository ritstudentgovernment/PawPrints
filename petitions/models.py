""" 
models.py
Peter Zujko (pxz3370)
9/30/2016
"""
from django.db import models
from django.contrib.auth.models import User

#
# Defines petition model.
#
class Petition(models.Model):
    title = models.CharField(max_length=80)
    description = models.TextField()
    tags = models.ManyToManyField('petitions.Tag') 
    author = models.ForeignKey(User)
    signatures = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField()
    # Changed "published (bool)" field to an int field for flagging different states of the petition
    # These states include: 0 - new (unpublished), 1 - published, 2 - removed (unpublished)
    status = models.PositiveSmallIntegerField(default=0)
    # published = models.BooleanField(default=False)
    expires = models.DateTimeField()
    last_signed = models.DateTimeField(default=None, blank=True, null=True)
    has_response = models.BooleanField(default=False)
    response = models.ForeignKey('petitions.Response', default=None, blank=True, null=True)

    def __unicode__(self):
        return self.title

#
# Defines tag model.
#
class Tag(models.Model):
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name

#
# Defines a response model.
#
class Response(models.Model):
    description = models.TextField()
    created_at = models.DateTimeField()
    author = models.TextField()

    def __unicode__(self):
        return self.author
