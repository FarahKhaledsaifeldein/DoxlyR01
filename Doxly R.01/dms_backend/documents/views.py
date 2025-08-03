from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend

from django.db.models import Q
from .models import Document, DocumentShare
from .serializers import (
    DocumentSerializer,
    DocumentUploadSerializer,
    DocumentShareSerializer
)
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
from django.utils import timezone
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend

User = get_user_model()

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Document
from .serializers import DocumentSerializer, DocumentUploadSerializer
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from projects.models import Project  # Add this import
import os
from rest_framework import serializers
# documents/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import Document
from django.shortcuts import get_object_or_404


class DocumentShareView(APIView):
    """Handle document sharing"""
    permission_classes = [permissions.IsAuthenticated]
    

    def post(self, request, document_id):
        document = get_object_or_404(Document, pk=document_id)#, owner=request.user
        
        
        # Check if user has permission to share this document
        if document.uploaded_by != request.user and not request.user.has_perm('documents.share_document'):
            return Response(
                {'error': 'You do not have permission to share this document'},
                status=status.HTTP_403_FORBIDDEN
            )

        shared_with_email = request.data.get('shared_with')
        permission_level = request.data.get('permission_level', 'view')
        expires_in = request.data.get('expires_in')  # in days

        try:
            shared_with = User.objects.get(email=shared_with_email)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        expires_at = None
        if expires_in:
            expires_at = timezone.now() + timedelta(days=int(expires_in))

        share, created = DocumentShare.objects.get_or_create(
            document=document,
            shared_with=shared_with,
            defaults={
                'shared_by': request.user,
                'permission_level': permission_level,
                'expires_at': expires_at
            }
        )

        if not created:
            share.permission_level = permission_level
            share.expires_at = expires_at
            share.save()

        return Response(
            DocumentShareSerializer(share).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )

class SharedDocumentListView(generics.ListAPIView):
    """List documents shared with current user"""
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Document.objects.filter(
            shares__shared_with=self.request.user,
            shares__is_active=True,
            shares__expires_at__gte=timezone.now() if not None else True
        ).distinct()

class DocumentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Enhanced document detail view with sharing check"""
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [permissions.IsAuthenticated()]
        return super().get_permissions()

    def check_object_permissions(self, request, obj):
        super().check_object_permissions(request, obj)
        
        # Allow access if:
        # 1. User is owner
        # 2. Document is shared with user
        # 3. User has view permission through sharing
        if (obj.uploaded_by != request.user and 
            not obj.shares.filter(shared_with=request.user, is_active=True).exists()):
            self.permission_denied(
                request,
                message="You don't have permission to access this document",
                code=status.HTTP_403_FORBIDDEN
            )



# In views.py
from rest_framework.pagination import PageNumberPagination

class DocumentSearchView(generics.ListAPIView):
    serializer_class = DocumentSerializer
    pagination_class = PageNumberPagination  # Add pagination
    filter_backends = [SearchFilter]
    search_fields = ['name', 'description', 'file_name']
    
    def get_queryset(self):
        queryset = Document.objects.all()
        search_term = self.request.query_params.get('search')
        
        if search_term:
            queryset = queryset.filter(
                Q(name__icontains=search_term) |
                Q(description__icontains=search_term) |
                Q(file_name__icontains=search_term)
            )
        return queryset

    
# List Documents (GET)
class DocumentListView(generics.ListAPIView):
    """
    GET /documents/
    Lists all documents with search/filter capabilities.
    """
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ['name', 'description', 'file__name']
    filterset_fields = ['project_id', 'uploaded_by', 'file_type']

# Upload Document (POST)


from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import Document
from .serializers import DocumentUploadSerializer
from projects.models import Project
import os
from datetime import datetime, timedelta
from django.utils import timezone


class DocumentUploadView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def validate_project_id(self, value):
        """Validate project exists if provided"""
        if value and not Project.objects.filter(id=value).exists():
            raise ValidationError("Project does not exist")
        return value

    def post(self, request):
        # Ensure we're getting multipart form data
        if not request.content_type.startswith('multipart/form-data'):
            return Response(
                {"error": "Content-Type must be multipart/form-data"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check for required file
        if 'file' not in request.FILES:
            return Response(
                {"error": "No file provided"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Process form data directly (no need to copy POST)
            file = request.FILES['file']
            name = request.POST.get('name')
            project_id = request.POST.get('project_id')
            is_encrypted = request.POST.get('is_encrypted', 'false').lower() == 'true'

            # Validate project if provided
            if project_id:
                try:
                    project_id = int(project_id)
                    self.validate_project_id(project_id)
                except (ValueError, ValidationError) as e:
                    return Response(
                        {"error": "Invalid project ID"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            # Create document instance
            file_name_without_ext = os.path.splitext(file.name)[0]
            document = Document(
                file=file,
                uploaded_by=request.user,
                file_size=file.size,
                file_type=file.name.split('.')[-1],
                is_encrypted=is_encrypted,
                name=name or file_name_without_ext,
                project_id=project_id or Project.get_default_project(request.user).id
            )
            
            document.save()

            # Set default name if not provided
            if not name:
                document.name = f"{file_name_without_ext}_{document.id}"
                document.save()

            if document.is_encrypted:
                document.encrypt_document()

            return Response({
                "doc_id": document.doc_id,
                "name": document.name,
                "project": document.project.name if document.project else None,
                "file_url": document.file.url,
                "file_size": document.file_size,
                "is_encrypted": document.is_encrypted
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {"error": f"Server error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )