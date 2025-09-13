import jwt
from django.conf import settings
from rest_framework import authentication, exceptions
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta

User = get_user_model()

class JWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return None
            
        token = auth_header.split(' ')[1]
        
        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
            user_id = payload.get('user_id')
            
            if not user_id:
                raise exceptions.AuthenticationFailed('Token invalide')
                
            user = User.objects.get(id=user_id)
            
            if not user.is_active:
                raise exceptions.AuthenticationFailed('Compte désactivé')
                
            return (user, token)
            
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Token expiré')
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed('Token invalide')
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed('Utilisateur non trouvé')

def generate_jwt_token(user):
    """Generate JWT token for user"""
    payload = {
        'user_id': user.id,
        'email': user.email,
        'role': user.role,
        'exp': datetime.utcnow() + settings.JWT_EXPIRATION_DELTA,
        'iat': datetime.utcnow()
    }
    
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)