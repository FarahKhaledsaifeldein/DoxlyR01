from django.db import models

class StorageLocation(models.Model):
    """Represents where a document is stored (local, cloud)."""
    STORAGE_TYPES = [
        ('local', 'Local Server'),
        ('aws_s3', 'AWS S3'),
        ('gdrive', 'Google Drive'),
    ]
    
    document_id = models.UUIDField(unique=True)
    storage_type = models.CharField(max_length=10, choices=STORAGE_TYPES)
    file_path = models.CharField(max_length=500)  # Local path or cloud URL
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Storage for Document {self.document_id} - {self.storage_type}"
