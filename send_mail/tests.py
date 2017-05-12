from django.core import mail
from django.test import TestCase, Client
from django.contrib.auth.models import User
from petitions.models import Petition, Tag
from profile.models import Profile
from datetime import timedelta
from django.utils import timezone
from send_mail.tasks import *

class EmailTests(TestCase):
    def setUp(self):
        self.tag = Tag(name='test')
        self.tag.save()
        self.user = User.objects.create_user(username='testuser', email='tesetuser@something.com')
        self.user.save()
        self.petition = Petition(title='test petition', description='This is a test petition', author=self.user,created_at=timezone.now(),status=1, expires=timezone.now()+timedelta(days=30))
        self.petition.save()
        self.user.profile.petitions_signed.add(self.petition)

    def test_petition_approved(self):
        petition_approved(self.petition.id, 'test_path')

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'PawPrints - Petition approved.')

    def test_petition_rejected(self):
        petition_rejected(self.petition.id, 'test_path')

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'PawPrints - Petition rejected')

    def test_petition_update(self):
        petition_update(self.petition.id, 'test_path')

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'PawPrints - Petition status update')

    def test_petition_reached(self):
        petition_reached(self.petition.id, 'test_path')

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'PawPrints - Petition threshold reached')

    def test_petition_received(self):
        petition_received(self.petition.id, 'test_path')

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'PawPrints - Petition received')
