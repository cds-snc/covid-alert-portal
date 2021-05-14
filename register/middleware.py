from basicauth.basicauthutils import validate_request
from basicauth.compat import MiddlewareMixin
from basicauth.response import HttpResponseUnauthorized


class BasicAuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.path == '/status/':
            return None

        if not validate_request(request):
            return HttpResponseUnauthorized()
        return None
    
