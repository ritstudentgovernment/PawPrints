"""
Author: Peter Zujko (@zujko)
Description: Tests for profile operations.
Date Created: Nov 7 2016
Updated: Nov 8 2016
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User

class ProfileTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.testUser = User.objects.create_user(username='txu1267', email='txu1267@rit.edu')
        self.testUser.set_password('test')
        self.testUser.save()

    def test_update_notification(self):
        self.client.force_login(self.testUser)
        response = self.client.post('/profile/settings/notifications/'+str(self.testUser.id), {'response': '0'})
        user = User.objects.get(id=self.testUser.id)
        self.assertEqual(user.profile.notifications.update, False)
