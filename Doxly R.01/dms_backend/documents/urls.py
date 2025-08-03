from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView,TokenObtainPairView,TokenVerifyView
from .views import (
    DocumentListView,
    DocumentSearchView,
    DocumentDetailView,
    DocumentUploadView,
    DocumentShareView,
    SharedDocumentListView,
  
    
)

urlpatterns = [
    # Document CRUD endpoints
    path('', DocumentListView.as_view(), name='document-list'),
    path('<int:pk>/', DocumentDetailView.as_view(), name='document-detail'),
    path('upload/', DocumentUploadView.as_view(), name='document-upload'),
    
    # Document sharing endpoints
    path('<int:document_id>/share/', DocumentShareView.as_view(), name='document-share'),
    path('shared/', SharedDocumentListView.as_view(), name='shared-documents'),
    
    # Document versioning
    #path('<int:document_id>/versions/', DocumentVersionListView.as_view(), name='document-versions'),
    
    # File operations
    #path('<int:pk>/download/', DocumentDownloadView.as_view(), name='document-download'),
    
    # Search and filtering
    path('search/', DocumentSearchView.as_view(), name='document-search'),
    
  # Add these token endpoints:
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # If you want to verify tokens:
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),

]


