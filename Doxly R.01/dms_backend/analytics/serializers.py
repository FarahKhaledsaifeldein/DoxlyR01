from rest_framework import serializers
from .models import DocumentAnalysis

class DocumentAnalysisSerializer(serializers.ModelSerializer):
    """Serializer for AI-based document analysis results."""
    class Meta:
        model = DocumentAnalysis
        fields = '__all__'
