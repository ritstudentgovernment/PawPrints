"""
Author: Peter Zujko (@zujko)
Description: Tests for profile operations.
Date Created: Nov 7 2016
Updated: Nov 8 2016
"""
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.test import Client, TestCase


class ProfileTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.testUser = User.objects.create_user(
            username='txu1267', email='txu1267@rit.edu')
        self.testUser.set_password('test')
        self.testUser.save()
        self.superUser = User.objects.create_user(
            username='txu1266', email='txu1266', is_superuser=True)
        self.superUser.set_password('test')
        self.superUser.save()
        self.superUser2 = User.objects.create_user(
            username='txu1265', email='txu1265', is_superuser=True, is_staff=True)
        self.superUser2.set_password('test')
        self.superUser2.save()
        self.user = User.objects.create_user(
            username='axu7254', email='axu7254')
        self.user2 = User.objects.create_user(
            username='cxl1234', email='cxl1234')
        self.user3 = User.objects.create_user(
            username='abc4321', email='abc4321')

    def test_logout(self):
        self.client.force_login(self.testUser)
        # Since they are logged in, they should be able to update
        response = self.client.post(
            '/profile/settings/notifications/'+str(self.testUser.id), {'response': '0'})
        self.assertEqual(response.getvalue().decode("utf-8"), str(True))

        # Logout
        response = self.client.get('/logout/')
        self.assertEqual(response.status_code, 302)

    def test_profile_created(self):
        self.assertEqual(self.user.profile.__unicode__(), self.user.username)

    def test_update_notification(self):
        self.client.force_login(self.testUser)
        response = self.client.post(
            '/profile/settings/notifications/'+str(self.testUser.id), {'response': '0'})
        user = User.objects.get(id=self.testUser.id)
        self.assertEqual(user.profile.notifications.update, False)

        # Make sure other people can't update users notifications
        response = self.client.post(
            '/profile/settings/notifications/99999', {'response': '0'})
        self.assertEqual(response.getvalue().decode("utf-8"), str(False))

    def test_profile_page(self):
        self.client.force_login(self.testUser)
        response = self.client.get('/profile/')
        self.assertEqual(response.status_code, 200)

    def test_add_superuser(self):
        self.client.force_login(self.superUser)
        response = self.client.post(
            '/profile/manage/admin/add/' + str(self.user2.id))
        user = User.objects.get(id=self.user2.id)
        self.assertEqual(user.is_superuser, True)
        self.assertEqual(user.is_staff, True)
        self.assertEqual(response.status_code, 200)

    def test_add_superuser_fail(self):
        self.client.force_login(self.user)
        response = self.client.post(
            '/profile/manage/admin/add/' + str(self.user2.id))
        user = User.objects.get(id=self.user2.id)
        self.assertEqual(user.is_superuser, False)
        self.assertEqual(user.is_staff, False)
        self.assertEqual(response.status_code, 403)

    def test_add_staff(self):
        self.client.force_login(self.superUser)
        response = self.client.post(
            '/profile/manage/manager/add/' + str(self.user2.id))
        user = User.objects.get(id=self.user2.id)
        self.assertEqual(user.is_staff, True)
        self.assertEqual(response.status_code, 200)

    def test_add_staff_fail(self):
        self.client.force_login(self.user)
        response = self.client.post(
            '/profile/manage/manager/add/' + str(self.user2.id))
        user = User.objects.get(id=self.user2.id)
        self.assertEqual(user.is_staff, False)
        self.assertEqual(response.status_code, 403)

    def test_remove_superuser(self):
        self.client.force_login(self.superUser)
        response = self.client.post(
            '/profile/manage/admin/remove/' + str(self.superUser2.id))
        user = User.objects.get(id=self.superUser2.id)
        self.assertEqual(user.is_superuser, False)
        #self.assertEqual(user.is_staff, False)
        self.assertEqual(response.status_code, 200)

    def test_remove_superuser_fail(self):
        self.client.force_login(self.user)
        response = self.client.post(
            '/profile/manage/admin/remove/' + str(self.superUser2.id))
        user = User.objects.get(id=self.superUser2.id)
        self.assertEqual(user.is_superuser, True)
        self.assertEqual(user.is_staff, True)
        self.assertEqual(response.status_code, 403)

    def test_remove_staff(self):
        self.client.force_login(self.superUser)
        response = self.client.post(
            '/profile/manage/manager/remove/' + str(self.superUser2.id))
        user = User.objects.get(id=self.superUser2.id)
        self.assertEqual(user.is_staff, False)
        self.assertEqual(response.status_code, 200)

    def test_remove_staff_fail(self):
        self.client.force_login(self.user)
        response = self.client.post(
            '/profile/manage/manager/remove/' + str(self.superUser2.id))
        user = User.objects.get(id=self.superUser2.id)
        self.assertEqual(user.is_staff, True)
        self.assertEqual(response.status_code, 403)

    def test_access_admin_panel(self):
        self.client.force_login(self.superUser)
        response = self.client.post('/profile/manage/admin')
        self.assertEqual(response.status_code, 200)

    def test_access_admin_panel_fail(self):
        self.client.force_login(self.user)
        response = self.client.post('/profile/manage/admin')
        self.assertEqual(response.status_code, 302)
