from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.conf import settings
from django.views.generic import View
from django.http import HttpResponse, HttpResponseServerError, HttpResponseBadRequest, HttpResponseNotFound
from .util import prepare_django_request
from onelogin.saml2.settings import OneLogin_Saml2_Settings
from onelogin.saml2.auth import OneLogin_Saml2_Auth
from onelogin.saml2.utils import OneLogin_Saml2_Utils


class SettingsMixin(object):
    def get_settings(self):
        return OneLogin_Saml2_Settings(settings=None, custom_base_path=settings.SAML_FOLDER, sp_validation_only=True)


class InitAuthView(SettingsMixin, View):
    def get(self, *args, **kwargs):
        request = prepare_django_request(self.request)
        auth = OneLogin_Saml2_Auth(request, self.get_settings())

        return_url = self.request.GET.get('next', settings.LOGIN_REDIRECT_URL)

        return redirect(auth.login(return_to=return_url))


class CompleteAuthView(SettingsMixin, View):
    def get(self, request):
        return HttpResponseNotFound()

    def post(self, request):
        req = prepare_django_request(request)
        auth = OneLogin_Saml2_Auth(req, self.get_settings())

        auth.process_response()

        errors = auth.get_errors()

        if not errors:
            if auth.is_authenticated:
                user = authenticate(request, saml_authentication=auth)
                login(self.request, user)
                if 'RelayState' in req['post_data'] and OneLogin_Saml2_Utils.get_self_url(req) != req['post_data'][
                        'RelayState']:
                    return redirect(auth.redirect_to(req['post_data']['RelayState']))
                else:
                    return redirect('/')
            else:
                raise PermissionDenied()
        else:
            if settings.DEBUG:
                print(auth.get_last_error_reason())
            return HttpResponseBadRequest("Erro processing SAML response ".join(errors))


class MetadataView(SettingsMixin, View):
    def get(self, request, *args, **kwargs):
        req = prepare_django_request(request)
        auth = OneLogin_Saml2_Auth(req, self.get_settings())
        saml_settings = auth.get_settings()
        metadata = saml_settings.get_sp_metadata()
        errors = saml_settings.validate_metadata(metadata)

        if len(errors) == 0:
            return HttpResponse(content=metadata, content_type='text/xml')
        return HttpResponseServerError(content=', '.join(errors))
