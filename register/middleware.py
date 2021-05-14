from basicauth.basicauthutils import validate_request
from basicauth.compat import MiddlewareMixin
from basicauth.response import HttpResponseUnauthorized


class BasicAuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if 'status' in request.path:
            return None

        if not validate_request(request):
            return HttpResponseUnauthorized()
        return None
    
