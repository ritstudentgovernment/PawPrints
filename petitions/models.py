from django.db import models
from django.contrib.auth.models import User


class Petition(models.Model):
    title = models.CharField(max_length=80)
    description = models.TextField()
    tags = models.ManyToManyField(Tag) 
    author = models.ForeignKey(User)
    signatures = models.PositiveIntegerField()

    def __unicode__(self):
        return self.title


class Tag(models.Model):
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name
