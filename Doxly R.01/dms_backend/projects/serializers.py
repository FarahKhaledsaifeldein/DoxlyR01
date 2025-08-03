from rest_framework import serializers
from .models import Project, FolderStructure

class FolderStructureSerializer(serializers.ModelSerializer):
    """Serializer for folder structure within projects."""
    class Meta:
        model = FolderStructure
        fields = '__all__'

class ProjectSerializer(serializers.ModelSerializer):
    """Serializer for Project model."""
    folders = FolderStructureSerializer(many=True, read_only=True)
    
    def create(self, validated_data):
        #project = super().create(validated_data)
        project = Project(**validated_data)
        project.save() 
        project.folder_path = f"/projects/{project.id}/"
        project.save(update_fields=['folder_path'])
        return project

    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = ['id', 'created_by', 'created_at', 'folder_path']
        extra_kwargs = {
            'folder_path': {'required': False}  # Not mandatory
        }
