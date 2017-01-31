""" 
Author: Peter Zujko (@zujko)
        Lukas Yelle (@lukasyelle)
Description: Contains models for Petition, Tag, and Response.
Date Created: Sept 15 2016
Updated: Oct 17 2016
"""
from django.db import models
from django.contrib.auth.models import User
from channels.binding.websockets import WebsocketBinding

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
    # These states include: 0 - new (unpublished), 1 - published, 2 - removed (unpublished)
    status = models.PositiveSmallIntegerField(default=0)
    expires = models.DateTimeField()
    last_signed = models.DateTimeField(default=None, blank=True, null=True)
    has_response = models.BooleanField(default=False)
    response = models.ForeignKey('petitions.Response', default=None, blank=True, null=True) 
    # /in_progress = models.BooleanField(default=False)
    updates = models.ManyToManyField('petitions.Update', default=None)

    def __str__(self):
        return self.title



class PetitionBinding(WebsocketBinding):

    model = Petition
    stream = "petitions"
    fields = ["title",
              "description",
              "author",
              "signatures",
              "status",
              "last_signed"]

    @classmethod
    def group_names(cls, instance):
        return ["petition"]

    def has_permission(self, user, action, pk):
        return True


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
