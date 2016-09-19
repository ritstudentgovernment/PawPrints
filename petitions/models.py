from django.db import models
from django.contrib.auth.models import User

#
# Defines petition model.
#
class Petition(models.Model):
    title = models.CharField(max_length=80)
    description = models.TextField()
    tags = models.ManyToManyField(Tag) 
    author = models.ForeignKey(User)
    signatures = models.PositiveIntegerField()
    created_at = models.DateTimeField()
    published = models.BooleanField(default=False)
    expires = models.DateTimeField()
    last_signed = models.DateTimeField()
    has_response = models.BooleanField(default=False)
    response = models.ForeignKey(Response, default=None, blank=True, null=True)

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
