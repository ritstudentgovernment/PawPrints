"""
auth_backend.py
Peter Zujko (@zujko)

Defines Django authentication backend for shibboleth.

04/05/17
"""
from django.contrib.auth.models import User


class Attributes():
    EDU_AFFILIATION = 'urn:oid:1.3.6.1.4.1.4447.1.41'
    FIRST_NAME = 'urn:oid:2.5.4.42'
    LAST_NAME = 'urn:oid:2.5.4.4'
    USERNAME = 'urn:oid:0.9.2342.19200300.100.1.1'


class SAMLSPBackend(object):
    def authenticate(self, request, saml_authentication=None):
        if not saml_authentication:
            return None

        if saml_authentication.is_authenticated():
            attributes = saml_authentication.get_attributes()

            username = attributes[Attributes.USERNAME][0]
            first_name = attributes[Attributes.FIRST_NAME][0]
            last_name = attributes[Attributes.LAST_NAME][0]
            affiliation = attributes.get(Attributes.EDU_AFFILIATION, ['-1'])

            try:
                # Grab attributes from shib and auth user
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                # If user does not exist in DB, Create a user object and save to DB
                user = User(username=username, email=username + "@rit.edu")
                user.set_unusable_password()

            user.first_name = first_name
            user.last_name = last_name
            user.save()

            # Set user profile attributes
            user.profile.full_name = "{} {}".format(first_name, last_name)
            user.profile.display_name = "{}{}".format(
                first_name[0], last_name[0])

            # Set user Affiliation
            user.profile.has_access = 0
            if 'Student' in affiliation in affiliation:
                 user.profile.has_access = 1

            user.profile.save()

            return user

        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
