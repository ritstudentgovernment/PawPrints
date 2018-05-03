from profile.models import Notifications, Profile

from django.contrib.auth.models import User
from django.test import TestCase
#from onelogin.saml2.auth import OneLogin_Saml2_Auth

from .auth_backend import SAMLSPBackend, Attributes
from unittest.mock import patch


class AuthBackendTestCase(TestCase):
    def setUp(self):
        user = User.objects.create(username='txu1111', email='txu1111@rit.edu')
        Profile.objects.all().delete()
        Profile.objects.create(user=user,
                               notifications=Notifications.objects.create())

    @patch('onelogin.saml2.auth.OneLogin_Saml2_Auth')
    def test_authenticate_method_student(self, auth_mock):
        user = User.objects.get(username='txu1111')
        saml_backend = SAMLSPBackend()

        # Test that user exists
        attrs_student = {Attributes.USERNAME: [user.username], Attributes.FIRST_NAME: [
            'Test'], Attributes.LAST_NAME: ['User'], Attributes.EDU_AFFILIATION: {'Student'}}
        auth_mock.get_attributes.return_value = attrs_student

        auth_user = saml_backend.authenticate(saml_authentication=auth_mock)

        assert auth_user.profile.full_name == 'Test User'
        assert auth_user.profile.has_access == 1
        assert auth_user.profile.display_name == 'TU'

    @patch('onelogin.saml2.auth.OneLogin_Saml2_Auth')
    def test_authenticate_method_alumni(self, auth_mock):
        saml_backend = SAMLSPBackend()

        # Test alumni account
        attrs_alumni = {Attributes.USERNAME: ['alum1234'], Attributes.FIRST_NAME: [
            'Alumni'], Attributes.LAST_NAME: ['User'], Attributes.EDU_AFFILIATION: {'Alumni'}}
        auth_mock.get_attributes.return_value = attrs_alumni

        assert not User.objects.filter(username='alum1234').exists()

        auth_user = saml_backend.authenticate(saml_authentication=auth_mock)
        assert User.objects.filter(username='alum1234').exists()
        assert auth_user.profile.full_name == 'Alumni User'
        assert auth_user.profile.has_access == 0
        assert auth_user.profile.display_name == 'AU'

    def test_get_user(self):
        saml_backend = SAMLSPBackend()

        assert saml_backend.get_user(999999) == None

        user = User.objects.get(username='txu1111')

        assert saml_backend.get_user(user.id) == user
