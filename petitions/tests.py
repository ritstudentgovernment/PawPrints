# """
# Author: Peter Zujko (@zujko)
# Author: Chris Lemelin (@chrislemelin)
# Description: Tests for petition operations.
# Date Created: Sept 15 2016
# Updated: Feb 17 2017
# """
# from datetime import timedelta

# from django.contrib.auth.models import User
# from django.test import Client, TestCase
# from django.test.client import RequestFactory
# from django.utils import timezone

# from petitions.models import Petition, Response, Tag, Update

# from .consumers import get_petitions_and_map
# from .views import (PETITION_DEFAULT_BODY, PETITION_DEFAULT_TITLE, edit_check,
#                     get_petition, petition_edit, petition_sign, petition_report)


# class PetitionTest(TestCase):
#     def setUp(self):
#         self.client = Client()
#         self.factory = RequestFactory()
#         self.superUser = User.objects.create_user(
#             username='txu1267', email='txu1267', is_staff=True)
#         self.superUser.set_password('test')
#         self.superUser.save()
#         self.superUser2 = User.objects.create_user(
#             username='txu1266', email='txu1266', is_superuser=True)
#         self.superUser2.set_password('test')
#         self.superUser2.save()
#         self.user = User.objects.create_user(
#             username='axu7254', email='axu7254')
#         self.user2 = User.objects.create_user(
#             username='cxl1234', email='cxl1234')
#         self.user3 = User.objects.create_user(
#             username='abc4321', email='abc4321')
#         self.tag = Tag(name='Test')
#         self.tag.save()
#         self.petition = Petition(title='Test petition',
#                                  description='This is a test petition',
#                                  author=self.user,
#                                  created_at=timezone.now(),
#                                  status=0,
#                                  expires=timezone.now() + timedelta(days=30)
#                                  )
#         self.petition.save()
#         self.petition.tags.add(self.tag)
#         self.petitionPublished = Petition(title='Test petition Published',
#                                           description='This is a test petition Published',
#                                           author=self.user2,
#                                           created_at=timezone.now(),
#                                           status=1,
#                                           expires=timezone.now() + timedelta(days=30)
#                                           )
#         self.petitionPublished.save()

#     def test_about_page(self):
#         response = self.client.get('/about/')
#         assert response.status_code == 200
#         self.assertTemplateUsed(response, 'about.html')

#     def test_maintenance_page(self):
#         response = self.client.get('/maintenance/')
#         assert response.status_code == 200
#         self.assertTemplateUsed(response, 'Something_Special.html')

#     def test_index_page(self):
#         response = self.client.get('/')
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'index.html')

#     def test_404(self):
#         response = self.client.get('/doesnotexist')
#         self.assertEqual(response.status_code, 404)
#         self.assertTemplateUsed(response, '404.html')

#     def test_petition_edit(self):
#         self.client.force_login(self.user)
#         # Change petition title to 'New'
#         obj = {
#             "attribute": "title",
#             "value": "New"
#         }
#         response = self.client.post(
#             '/petition/update/' + str(self.petition.id), obj)
#         # Check that it doesn't 404
#         self.assertNotEqual(response.status_code, 404)
#         # Check that petition was actually changed
#         pet = Petition.objects.get(pk=self.petition.id)
#         self.assertEqual(pet.title, 'New')

#     def test_petition_publish(self):
#         self.client.force_login(self.user)
#         tag = Tag(name='test tag')
#         tag.save()
#         obj = {
#             "attribute": "publish",
#             "value": "foo"
#         }
#         self.petition.status = 0
#         self.petition.tags.add(tag)
#         self.petition.save()
#         request = self.factory.post(
#             '/petition/update/' + str(self.petition.id), obj)
#         request.META['HTTP_HOST'] = 'localhost'
#         request.user = self.user
#         response = petition_edit(request, self.petition.id)
#         # Make sure there is no 404
#         self.assertNotEqual(response.status_code, 404)
#         # Check that petition was published
#         pet = Petition.objects.get(pk=self.petition.id)
#         self.assertEqual(pet.status, 1)

#     def test_sign_petition(self):
#         self.client.force_login(self.superUser)
#         response = self.client.post(
#             '/petition/sign/' + str(self.petitionPublished.id), {'test': 'test'})
#         pet = Petition.objects.get(pk=self.petitionPublished.id)
#         self.assertEqual(pet.signatures, 1)
#         self.assertEqual(response.status_code, 200)

#     def test_petition_subscribe(self):
#         self.client.force_login(self.user)
#         user = User.objects.get(pk=self.user.id)
#         self.assertEqual(user.profile.subscriptions.filter(
#             pk=self.petition.id).exists(), False)
#         response = self.client.post(
#             '/petition/subscribe/' + str(self.petition.id), {})
#         user = User.objects.get(pk=self.user.id)

#         self.assertEqual(user.profile.subscriptions.filter(
#             pk=self.petition.id).exists(), True)

#     def test_petition_unsubscribe(self):
#         self.client.force_login(self.user)
#         user = User.objects.get(pk=self.user.id)
#         self.assertEqual(user.profile.subscriptions.filter(
#             pk=self.petition.id).exists(), False)
#         response = self.client.post(
#             '/petition/subscribe/' + str(self.petition.id), {})
#         user = User.objects.get(pk=self.user.id)

#         self.assertEqual(user.profile.subscriptions.filter(
#             pk=self.petition.id).exists(), True)

#         response = self.client.post(
#             '/petition/unsubscribe/' + str(self.petition.id), {})
#         user = User.objects.get(pk=self.user.id)

#         self.assertEqual(user.profile.subscriptions.filter(
#             pk=self.petition.id).exists(), False)

#     def test_petition_unpublish(self):
#         self.client.force_login(self.superUser)
#         response = self.client.post(
#             '/petition/unpublish/' + str(self.petition.id))
#         self.assertEqual(response.status_code, 200)
#         pet = Petition.objects.get(pk=self.petition.id)
#         self.assertEqual(pet.status, 2)

#         # Test using not super user
#         self.client.force_login(self.user)
#         pet.status = 1
#         pet.save()
#         response = self.client.post(
#             '/petition/unpublish/' + str(self.petition.id))
#         pet = Petition.objects.get(pk=self.petition.id)
#         self.assertEqual(pet.status, 1)

#     def test_petition_page(self):
#         response = self.client.get('/petition/' + str(self.petition.id))
#         self.assertEqual(response.status_code, 200)

#     def test_url_redirect_fail(self):
#         self.client.force_login(self.user)
#         response = self.client.get('/petition/' + str(666))
#         self.assertEqual(response.status_code, 404)

#     def test_create_petition(self):
#         self.client.force_login(self.user)
#         response = self.client.post('/petition/create/')
#         self.assertEqual(response.status_code, 200)
#         userobj = User.objects.get(pk=self.user.id)
#         self.assertEqual(userobj.profile.petitions_signed.all()[
#                          0].title, PETITION_DEFAULT_TITLE)

#     def test_check_edit(self):
#         self.client.force_login(self.user)
#         self.assertEqual(edit_check(self.user, self.petition), True)
#         self.assertEqual(edit_check(self.superUser, self.petition), False)
#         self.assertEqual(edit_check(self.superUser2, self.petition), False)
#         self.assertEqual(edit_check(self.user2, self.petition), False)

#     def test_serialize_petitions(self):
#         petitions = Petition.objects.all()
#         json_response = get_petitions_and_map(petitions)
#         # TODO: Improve this test to be more thorough
#         self.assertNotEqual(json_response, None)

#     def test_url_redirect(self):
#         self.client.force_login(self.user)
#         response = self.client.get('/petitions/' + str(self.petition.id))
#         self.assertEqual(response.status_code, 302)
#         self.assertRedirects(response, '/?p='+str(self.petition.id),
#                              status_code=302, target_status_code=200)

#     def test_edit_petition_description(self):
#         self.client.force_login(self.user)
#         obj = {
#             "attribute": "description",
#             "value": "test test test"
#         }
#         response = self.client.post(
#             '/petition/update/' + str(self.petition.id), obj)
#         self.assertNotEqual(response.status_code, 404)

#         pet = Petition.objects.get(pk=self.petition.id)
#         self.assertEqual(pet.description, "test test test")

#     def test_petition_add_tag(self):
#         self.client.force_login(self.user)
#         tag = Tag(name='test tag2')
#         tag.save()
#         obj = {
#             "attribute": "add-tag",
#             "value": tag.id
#         }

#         response = self.client.post(
#             '/petition/update/' + str(self.petition.id), obj)
#         self.assertNotEqual(response.status_code, 404)

#         pet = Petition.objects.get(pk=self.petition.id)
#         if tag not in pet.tags.all():
#             self.fail("tag not added")

#     def test_petition_remove_tag(self):
#         self.client.force_login(self.user)
#         tag = Tag(name='test tag2')
#         tag.save()
#         self.petition.tags.add(tag)
#         self.petition.save()
#         obj = {
#             "attribute": "remove-tag",
#             "value": tag.id
#         }

#         response = self.client.post(
#             '/petition/update/' + str(self.petition.id), obj)
#         self.assertNotEqual(response.status_code, 404)

#         pet = Petition.objects.get(pk=self.petition.id)
#         if tag in pet.tags.all():
#             self.fail("tag not removed")

#     def test_petition_add_update(self):
#         self.client.force_login(self.superUser)
#         obj = {
#             "attribute": "add_update",
#             "value": "test update"
#         }

#         request = self.factory.post(
#             '/petition/update/' + str(self.petition.id), obj)
#         request.user = self.superUser
#         request.META['HTTP_HOST'] = "random"
#         response = petition_edit(request, self.petition.id)
#         self.assertNotEqual(response.status_code, 404)

#         pet = Petition.objects.get(pk=self.petition.id)
#         fail = True
#         for update in pet.updates.all():
#             value = update.description
#             if value == "test update":
#                 fail = False
#         if fail:
#             self.fail("did not add update")

#     def test_petition_add_response(self):
#         self.client.force_login(self.superUser)
#         obj = {
#             "attribute": "response",
#             "value": "test response"
#         }

#         request = self.factory.post(
#             '/petition/update/' + str(self.petition.id), obj)
#         request.user = self.superUser
#         request.META['HTTP_HOST'] = "random"
#         response = petition_edit(request, self.petition.id)

#         self.assertNotEqual(response.status_code, 404)

#         pet = Petition.objects.get(pk=self.petition.id)
#         if pet.response.description != "test response":
#             self.fail()

#     def test_petition_mark_work_in_progress(self):
#         self.client.force_login(self.superUser)
#         obj = {
#             "attribute": "mark-in-progress"
#         }
#         self.assertEqual(self.petitionPublished.in_progress, None)

#         request = self.factory.post(
#             '/petition/update/' + str(self.petitionPublished.id), obj)
#         request.user = self.superUser
#         request.META['HTTP_HOST'] = "random"
#         response = petition_edit(request, self.petitionPublished.id)

#         self.assertNotEqual(response.status_code, 404)

#         pet = Petition.objects.get(pk=self.petitionPublished.id)
#         self.assertEqual(pet.in_progress, True)

#     def test_petition_unpublish_progress(self):
#         self.client.force_login(self.superUser)
#         obj = {
#             "attribute": "unpublish"
#         }
#         self.assertEqual(self.petitionPublished.status, 1)
#         request = self.factory.post(
#             '/petition/update/' + str(self.petitionPublished.id), obj)
#         request.user = self.superUser
#         request.META['HTTP_HOST'] = "random"
#         response = petition_edit(request, self.petitionPublished.id)
#         self.assertNotEqual(response.status_code, 404)

#         pet = Petition.objects.get(pk=self.petitionPublished.id)
#         self.assertEqual(pet.status, 2)

#     def report_petition(self, obj):
#         request = self.factory.post(
#             '/petition/report/' + str(self.petitionPublished.id), obj)
#         request.user = self.user
#         request.META['HTTP_HOST'] = "random"
#         return petition_report(request, self.petitionPublished.id)

#     def test_petition_report(self):
#         self.client.force_login(self.user)
#         obj = {
#             "reason": "Test reason"
#         }
#         response = self.report_petition(obj)
#         self.assertEqual(response.status_code, 200)
#         assert (response.content == b'true')
#         # an attempt to make a second report on the same petition will result in a `false` response
#         response_fail = self.report_petition(obj)
#         self.assertEqual(response_fail.status_code, 200)
#         assert (response_fail.content == b'false')

#     def test_get_petition(self):
#         self.client.force_login(self.superUser)
#         petition = get_petition(self.petition.id, self.user)
#         self.assertEqual(petition, self.petition)

#     def test_get_petition_fail(self):
#         self.client.force_login(self.superUser)
#         petition = get_petition(self.petition.id, self.user2)
#         self.assertEqual(petition, False)

#     def test_petition_str(self):
#         assert str(self.petition) == self.petition.title

#     def test_tag_str(self):
#         assert str(self.tag) == self.tag.name

#     def test_response_str(self):
#         resp = Response.objects.create(
#             description='Response', created_at=timezone.now(), author='Test Author')
#         assert str(resp) == 'Test Author'
