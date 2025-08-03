from rest_framework import serializers
from .models import StorageLocation

class StorageLocationSerializer(serializers.ModelSerializer):
    """Serializer for document storage locations."""
    
    class Meta:
        model = StorageLocation
        fields = '__all__'
