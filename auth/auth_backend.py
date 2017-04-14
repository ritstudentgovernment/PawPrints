from django.contrib.auth.models import User

class SAMLSPBackend(object):
    def authenticate(self, saml_authentication=None):
        if not saml_authentication:
            return None

        if saml_authentication.is_authenticated():
            attributes = saml_authentication.get_attributes()
            # TODO: Figure out correct attributes
            try:
                # Grab attributes from shib and auth user
                user = User.objects.get(username=saml_authentication.get_nameid())
            except User.DoesNotExist:
                # If user does not exist in DB, Create a user object and save to DB
                user = User(username=saml_authentication.get_nameid())
                user.set_unusable_password()
                # Set user attributes 
                user.email = attributes['email'][0]
                user.save()
            return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
