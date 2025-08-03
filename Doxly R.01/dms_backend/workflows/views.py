from rest_framework import generics, permissions
from .models import WorkflowStage, DocumentWorkflow
from .serializers import WorkflowStageSerializer, DocumentWorkflowSerializer

class WorkflowStageListCreateView(generics.ListCreateAPIView):
    """View for listing and creating workflow stages."""
    queryset = WorkflowStage.objects.all()
    serializer_class = WorkflowStageSerializer
    permission_classes = [permissions.IsAuthenticated]

class WorkflowStageDetailView(generics.RetrieveUpdateDestroyAPIView):
    """View for retrieving, updating, and deleting a workflow stage."""
    queryset = WorkflowStage.objects.all()
    serializer_class = WorkflowStageSerializer
    permission_classes = [permissions.IsAuthenticated]

class DocumentWorkflowListCreateView(generics.ListCreateAPIView):
    """View for listing and creating document workflows."""
    queryset = DocumentWorkflow.objects.all()
    serializer_class = DocumentWorkflowSerializer
    permission_classes = [permissions.IsAuthenticated]

class DocumentWorkflowDetailView(generics.RetrieveUpdateDestroyAPIView):
    """View for retrieving, updating, and deleting document workflows."""
    queryset = DocumentWorkflow.objects.all()
    serializer_class = DocumentWorkflowSerializer
    permission_classes = [permissions.IsAuthenticated]
