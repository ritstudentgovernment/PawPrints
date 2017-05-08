import logging
from datetime import datetime

logger = logging.getLogger('IPRequest')

class IPLogMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        logger.info('{} "{} {}" {}'.format(request.META.get('HTTP_X_FORWARDED_FOR'), request.META.get('REQUEST_METHOD'), request.META.get('PATH_INFO'), response.status_code))

        return response
