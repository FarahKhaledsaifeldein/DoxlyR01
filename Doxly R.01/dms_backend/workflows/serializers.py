from rest_framework import serializers
from .models import WorkflowStage, DocumentWorkflow

class WorkflowStageSerializer(serializers.ModelSerializer):
    """Serializer for workflow stages."""
    class Meta:
        model = WorkflowStage
        fields = '__all__'

class DocumentWorkflowSerializer(serializers.ModelSerializer):
    """Serializer for document workflow tracking."""
    class Meta:
        model = DocumentWorkflow
        fields = '__all__'
