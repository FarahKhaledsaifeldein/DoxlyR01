from rest_framework import serializers
from .models import EmailTemplate, NotificationMail

class EmailTemplateSerializer(serializers.ModelSerializer):
    """Serializer for managing email templates."""
    class Meta:
        model = EmailTemplate
        fields = '__all__'

class NotificationMailSerializer(serializers.ModelSerializer):
    """Serializer for tracking notifications sent to users."""
    class Meta:
        model = NotificationMail
        fields = '__all__'
        read_only_fields = ['created_at', 'sent_at']
