"""
Author: Peter Zujko (@zujko)
Description: Tests for petition operations.
Date Created: Sept 15 2016
Updated: Oct 26 2016
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from petitions.models import Petition, Tag
from datetime import timedelta
from django.utils import timezone
from .views import petition_sign

class PetitionTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.superUser = User.objects.create_user(username='txu1267', email='txu1267', is_staff=True)
        self.superUser.set_password('test')
        self.superUser.save()
        self.user = User.objects.create_user(username='axu7254', email='axu7254')
        self.tag = Tag(name='Test')
        self.tag.save()
        self.petition = Petition(title='Test petition',  
                description='This is a test petition', 
                author=self.user,
                created_at=timezone.now(),
                status=1,
                expires=timezone.now()+timedelta(days=30)
                )
        self.petition.save()

    def test_sign_petition(self):
        self.client.force_login(self.superUser)
        response = self.client.post('/petition/sign/'+str(self.petition.id), {'test':'test'})
        pet = Petition.objects.get(pk=self.petition.id)
        self.assertEqual(pet.signatures, 1)

    def test_petition_subscribe(self):
        self.client.force_login(self.user)
        user = User.objects.get(pk=self.user.id)
        self.assertEqual(user.profile.subscriptions.filter(pk=self.petition.id).exists(), False)
        response = self.client.post('/petition/subscribe/'+str(self.petition.id),{})
        user = User.objects.get(pk=self.user.id)
        
        self.assertEqual(user.profile.subscriptions.filter(pk=self.petition.id).exists(), True)

    def test_petition_unpublish(self):
        self.client.force_login(self.superUser)
        response = self.client.post('/petition/unpublish/'+str(self.petition.id))
        pet = Petition.objects.get(pk=self.petition.id)
        self.assertEqual(pet.status, 2)

        # Test using not super user
        self.client.force_login(self.user)
        pet.status = 1
        pet.save()
        response = self.client.post('/petition/unpublish/'+str(self.petition.id))
        pet = Petition.objects.get(pk=self.petition.id)
        self.assertEqual(pet.status, 1)

    def test_petition_page(self):
        response = self.client.get('/petition/'+str(self.petition.id))
        self.assertEqual(response.status_code, 200)

