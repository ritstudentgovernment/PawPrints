from django.test import TestCase, Client
from django.contrib.auth.models import User
from petitions.models import Petition, Tag
from datetime import timedelta
from django.utils import timezone
from channels import Channel
from channels.tests import ChannelTestCase

class EmailChannelTests(ChannelTestCase):
    def setUp(self):
        self.tag = Tag(name='test')
        self.tag.save()
        self.user = User.objects.create_user(username='testuser', email='tesetuser@something.com')
        self.user.save()
        self.petition = Petition(title='test petition', description='This is a test petition', author=self.user,created_at=timezone.now(),status=1, expires=timezone.now()+timedelta(days=30))
        self.petition.save()

    def test_email(self):
        print("SENDING")
        Channel("petition-approved").send({"petition_id": self.petition.id ,"petition_title": self.petition.title, "site_path": "localhost"})
