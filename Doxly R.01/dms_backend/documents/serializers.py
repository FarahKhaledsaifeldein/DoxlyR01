from rest_framework import serializers
from .models import Document, DocumentVersion, DocumentShare
import os

class DocumentShareSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentShare
        fields = '__all__'
        read_only_fields = ('shared_by', 'shared_at')

class DocumentUploadSerializer(serializers.Serializer):
    file = serializers.FileField(required=True)
    name = serializers.CharField(required=False, max_length=255, allow_blank=True, default=None)
    description = serializers.CharField(required=False, allow_blank=True, default=None)
    project_id = serializers.IntegerField(required=False, allow_null=True, default=None)
    is_encrypted = serializers.BooleanField(default=False)
    def validate_project_id(self, value):
        """Validate project exists if provided"""
        if value and not Project.objects.filter(id=value).exists():
            raise serializers.ValidationError("Project does not exist")
    def validate_file(self, value):
        valid_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx']
        ext = os.path.splitext(value.name)[1]
        if ext.lower() not in valid_extensions:
            raise serializers.ValidationError("Unsupported file type")
        return value

class DocumentVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentVersion
        fields = '__all__'

class DocumentSerializer(serializers.ModelSerializer):
    versions = DocumentVersionSerializer(many=True, read_only=True)
    shares = DocumentShareSerializer(many=True, read_only=True)
    file_url = serializers.SerializerMethodField()
    uploaded_by_name = serializers.SerializerMethodField()
    file_size_mb = serializers.SerializerMethodField()
    file_name = serializers.SerializerMethodField()
   
    doc_id = serializers.CharField(read_only=True) 

    def get_file_name(self, obj):
        return obj.file.name

    def get_unique_id(self, obj):
        return obj.id
    class Meta:
        model = Document
        fields = '__all__'
        read_only_fields = ('uploaded_by', 'uploaded_at', 'modified_at', 'reference_code')

    def get_file_url(self, obj):
        return obj.get_download_url()

    def get_uploaded_by_name(self, obj):
        return obj.uploaded_by.get_full_name() or obj.uploaded_by.email

    def get_file_size_mb(self, obj):
        return round(obj.file_size / (1024 * 1024), 2) if obj.file_size else 0
