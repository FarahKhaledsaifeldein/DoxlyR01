from rest_framework import generics, permissions
from .models import Project, FolderStructure
from .serializers import ProjectSerializer, FolderStructureSerializer


class ProjectListCreateView(generics.ListCreateAPIView):
    """View for listing and creating projects."""
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
      

    #permission_classes = [permissions.IsAuthenticated]

    

class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    """View for retrieving, updating, and deleting a project."""
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

class FolderStructureListCreateView(generics.ListCreateAPIView):
    """View for listing and creating folder structures within a project."""
    queryset = FolderStructure.objects.all()
    serializer_class = FolderStructureSerializer
    permission_classes = [permissions.IsAuthenticated]

class FolderStructureDetailView(generics.RetrieveUpdateDestroyAPIView):
    """View for retrieving, updating, and deleting folder structures."""
    queryset = FolderStructure.objects.all()
    serializer_class = FolderStructureSerializer
    permission_classes = [permissions.IsAuthenticated]
