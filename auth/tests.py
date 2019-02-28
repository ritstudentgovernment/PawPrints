from profile.models import Notifications, Profile
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase

from .auth_backend import Attributes, SAMLSPBackend
from .util import prepare_django_request


class AuthTestCase(TestCase):
    def setUp(self):
        user = User.objects.create(username='txu1111', email='txu1111@rit.edu')
        Profile.objects.all().delete()
        Profile.objects.create(user=user,
                               notifications=Notifications.objects.create())

    @patch('django.http.request')
    def test_prepare_util(self, request_mock):
        HOST = 'testhost'
        PORT = 5000
        PATH_INFO = 'info'
        # Attrs
        attrs_meta = {'HTTP_HOST': HOST,
                      'SERVER_PORT': PORT, 'PATH_INFO': PATH_INFO}
        get_attrs = {'test': 'test'}
        post_attrs = {'test': 'test_post'}

        request_mock.META = attrs_meta
        request_mock.GET = get_attrs
        request_mock.POST = post_attrs
        request_mock.is_secure.return_value = True

        prepared_request = prepare_django_request(request_mock)
        actual_req = {'https': 'on', 'http_host': HOST,
                      'script_name': PATH_INFO, 'get_data': get_attrs, 'post_data': post_attrs, 'server_port': PORT}
        assert prepared_request == actual_req

        # Test with not secure
        request_mock.is_secure.return_value = False
        prepared_request = prepare_django_request(request_mock)
        actual_req = {'https': 'off', 'http_host': HOST,
                      'script_name': PATH_INFO, 'get_data': get_attrs, 'post_data': post_attrs, 'server_port': PORT}
        assert prepared_request == actual_req

        # Test with HTTP_X_FORWARDED_FOR
        attrs_meta = {'HTTP_HOST': HOST,
                      'SERVER_PORT': PORT, 'PATH_INFO': PATH_INFO, 'HTTP_X_FORWARDED_FOR': 'testforward', 'HTTP_X_FORWARDED_PROTO': 'https'}
        request_mock.META = attrs_meta
        actual_req = {'https': 'on', 'http_host': HOST,
                      'script_name': PATH_INFO, 'get_data': get_attrs, 'post_data': post_attrs}
        prepared_request = prepare_django_request(request_mock)
        assert prepared_request == actual_req

    @patch('onelogin.saml2.auth.OneLogin_Saml2_Auth')
    def test_authenticate_method_student(self, auth_mock):
        user = User.objects.get(username='txu1111')
        saml_backend = SAMLSPBackend()

        # Test that user exists
        attrs_student = {Attributes.USERNAME: [user.username], Attributes.FIRST_NAME: [
            'Test'], Attributes.LAST_NAME: ['User'], Attributes.EDU_AFFILIATION: {'Student'}}
        auth_mock.get_attributes.return_value = attrs_student

        auth_user = saml_backend.authenticate(
            None, saml_authentication=auth_mock)

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

        auth_user = saml_backend.authenticate(
            None, saml_authentication=auth_mock)
        assert User.objects.filter(username='alum1234').exists()
        assert auth_user.profile.full_name == 'Alumni User'
        assert auth_user.profile.has_access == 0
        assert auth_user.profile.display_name == 'AU'

    @patch('onelogin.saml2.auth.OneLogin_Saml2_Auth')
    def test_authenticate_method_employee(self, auth_mock):
        saml_backend = SAMLSPBackend()

        # Test employee account
        attrs_emp = {Attributes.USERNAME: ['emp1234'], Attributes.FIRST_NAME: [
            'Employee'], Attributes.LAST_NAME: ['User'], Attributes.EDU_AFFILIATION: {'Alumni'}}
        auth_mock.get_attributes.return_value = attrs_emp

        assert not User.objects.filter(username='emp1234').exists()

        auth_user = saml_backend.authenticate(
            None, saml_authentication=auth_mock)
        assert User.objects.filter(username='emp1234').exists()
        assert auth_user.profile.full_name == 'Employee User'
        assert auth_user.profile.has_access == 0
        assert auth_user.profile.display_name == 'EU'

    # @patch('onelogin.saml2.auth.OneLogin_Saml2_Auth')
    # def test_authenticate_method_no_affiliation(self, auth_mock):
    #     saml_backend = SAMLSPBackend()
    #
    #     # Test no edu affiliation attr
    #     attrs_emp = {Attributes.USERNAME: ['emp1234'], Attributes.FIRST_NAME: [
    #         'Employee'], Attributes.LAST_NAME: ['User']}
    #     auth_mock.get_attributes.return_value = attrs_emp
    #
    #     assert not User.objects.filter(username='emp1234').exists()
    #
    #     auth_user = saml_backend.authenticate(
    #         None, saml_authentication=auth_mock)
    #     assert User.objects.filter(username='emp1234').exists()
    #     assert auth_user.profile.full_name == 'Employee User'
    #     assert auth_user.profile.has_access == 0
    #     assert auth_user.profile.display_name == 'EU'

    @patch('onelogin.saml2.auth.OneLogin_Saml2_Auth')
    def test_authenticate_method_not_authenticated(self, auth_mock):
        saml_backend = SAMLSPBackend()

        auth_mock.is_authenticated.return_value = False

        auth_user = saml_backend.authenticate(
            None, saml_authentication=auth_mock)

        assert auth_user == None

    def test_authenticate_method_none(self):
        saml_backend = SAMLSPBackend()

        auth_user = saml_backend.authenticate(None)
        assert auth_user == None

    def test_get_user(self):
        saml_backend = SAMLSPBackend()

        assert saml_backend.get_user(999999) == None

        user = User.objects.get(username='txu1111')

        assert saml_backend.get_user(user.id) == user
