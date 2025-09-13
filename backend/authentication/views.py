from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .serializers import UserRegistrationSerializer, UserLoginSerializer, UserSerializer
from .authentication import generate_jwt_token
import jwt
from django.conf import settings

User = get_user_model()

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register(request):
    """Register a new user"""
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token = generate_jwt_token(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'token': token,
            'message': 'Compte créé avec succès'
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login(request):
    """Login user"""
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        token = generate_jwt_token(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'token': token,
            'message': 'Connexion réussie'
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def profile(request):
    """Get current user profile"""
    return Response(UserSerializer(request.user).data)

@api_view(['PUT'])
def update_profile(request):
    """Update current user profile"""
    serializer = UserSerializer(request.user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def verify_token(request):
    """Verify if JWT token is valid"""
    token = request.data.get('token')
    
    if not token:
        return Response({
            'valid': False,
            'message': 'Token manquant'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id = payload.get('user_id')
        
        if not user_id:
            return Response({
                'valid': False,
                'message': 'Token invalide'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        user = User.objects.get(id=user_id)
        
        if not user.is_active:
            return Response({
                'valid': False,
                'message': 'Compte désactivé'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        return Response({
            'valid': True,
            'user': UserSerializer(user).data,
            'message': 'Token valide'
        })
        
    except jwt.ExpiredSignatureError:
        return Response({
            'valid': False,
            'message': 'Token expiré'
        }, status=status.HTTP_401_UNAUTHORIZED)
    except jwt.InvalidTokenError:
        return Response({
            'valid': False,
            'message': 'Token invalide'
        }, status=status.HTTP_400_BAD_REQUEST)
    except User.DoesNotExist:
        return Response({
            'valid': False,
            'message': 'Utilisateur non trouvé'
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def refresh_token(request):
    """Refresh JWT token"""
    token = request.data.get('token')
    
    if not token:
        return Response({
            'message': 'Token manquant'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Décoder le token même s'il est expiré pour récupérer l'utilisateur
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM], options={"verify_exp": False})
        user_id = payload.get('user_id')
        
        if not user_id:
            return Response({
                'message': 'Token invalide'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        user = User.objects.get(id=user_id)
        
        if not user.is_active:
            return Response({
                'message': 'Compte désactivé'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        # Générer un nouveau token
        new_token = generate_jwt_token(user)
        
        return Response({
            'token': new_token,
            'user': UserSerializer(user).data,
            'message': 'Token rafraîchi avec succès'
        })
        
    except jwt.InvalidTokenError:
        return Response({
            'message': 'Token invalide'
        }, status=status.HTTP_400_BAD_REQUEST)
    except User.DoesNotExist:
        return Response({
            'message': 'Utilisateur non trouvé'
        }, status=status.HTTP_404_NOT_FOUND)
