from django.utils.deprecation import MiddlewareMixin
from .authentication import JWTAuthentication

class JWTAuthenticationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Skip authentication for certain paths
        skip_paths = ['/admin/', '/api/auth/login/', '/api/auth/register/']
        
        if any(request.path.startswith(path) for path in skip_paths):
            return None
            
        # Try to authenticate using JWT
        authenticator = JWTAuthentication()
        result = authenticator.authenticate(request)
        
        if result:
            request.user, request.auth = result
            
        return None