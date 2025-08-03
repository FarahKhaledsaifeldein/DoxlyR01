from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet

# Use a router for viewsets
router = DefaultRouter()
router.register(r'', UserViewSet, basename='user')  # Add basename to ensure proper URL generation
# users/urls.py
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import CustomTokenObtainPairView

urlpatterns = [
    # JWT Authentication
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', include(router.urls)),
    
    # Existing user management
    #path('create/', CustomUserCreateView.as_view(), name='user_create'),
    # ... other user paths
]



'''from django.urls import path
from .views import UserListView

urlpatterns = [
    path("users/", UserListView.as_view(), name="user-list"),
]'''
