from datetime import datetime, timedelta
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model, authenticate
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSerializer, CustomTokenObtainPairSerializer
from rest_framework.views import APIView
from django.utils import timezone  # For timezone-aware datetimes

User = get_user_model()

class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom JWT login view that extends the default TokenObtainPairView
    to include additional user data in the response.
    """
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            try:
                user = User.objects.get(username=request.data['username'])
                expires_at = timezone.now() + timedelta(hours=2)
                
                response.data.update({
                    'user_id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'expires_at': expires_at.isoformat()
                })
                
                # Set HttpOnly cookie for additional security
                response.set_cookie(
                    'access_token',
                    response.data['access'],
                    httponly=True,
                    secure=True,  # For HTTPS
                    expires=expires_at,
                    samesite='Lax'
                )
                
            except User.DoesNotExist:
                return Response(
                    {"error": "User not found"},
                    status=status.HTTP_404_NOT_FOUND
                )

        return response

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing users.
    Provides registration endpoint for new users and JWT authentication.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_permissions(self):
        if self.action in ['register', 'login', 'refresh']:
            return [permissions.AllowAny()]
        return super().get_permissions()

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def login(self, request):
        """
        JWT login endpoint (replaces the previous token-based login)
        """
        view = CustomTokenObtainPairView.as_view()
        return view(request._request)

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def refresh(self, request):
        """
        JWT token refresh endpoint
        """
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response(
                {"error": "Refresh token is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            token = RefreshToken(refresh_token)
            access_token = str(token.access_token)
            
            # Set the same cookie as login for consistency
            expires_at = timezone.now() + timedelta(hours=2)
            response = Response({
                'access': access_token,
                'refresh': str(token),
                'expires_at': expires_at.isoformat()
            })
            
            response.set_cookie(
                'access_token',
                access_token,
                httponly=True,
                secure=True,
                expires=expires_at,
                samesite='Lax'
            )
            
            return response
            
        except Exception as e:
            return Response(
                {"error": "Invalid refresh token"},
                status=status.HTTP_401_UNAUTHORIZED
            )

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def register(self, request):
        """
        User registration endpoint
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Generate tokens for the new user
            refresh = RefreshToken.for_user(user)
            expires_at = timezone.now() + timedelta(hours=2)
            
            response = Response({
                "message": "Registration successful",
                "data": serializer.data,
                "tokens": {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                    'expires_at': expires_at.isoformat()
                }
            }, status=status.HTTP_201_CREATED)
            
            # Set HttpOnly cookie
            response.set_cookie(
                'access_token',
                str(refresh.access_token),
                httponly=True,
                secure=True,
                expires=expires_at,
                samesite='Lax'
            )
            
            return response
            
        return Response(
            {"message": "Registration failed", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

class LogoutView(APIView):
    """
    API endpoint for logging out users by blacklisting refresh tokens
    """
    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response(
                    {"error": "Refresh token is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            response = Response(
                {"message": "Logout successful"}, 
                status=status.HTTP_205_RESET_CONTENT
            )
            response.delete_cookie('access_token')
            return response
            
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )