from django.contrib import admin
from .models import StorageLocation

@admin.register(StorageLocation)
class StorageLocationAdmin(admin.ModelAdmin):
    list_display = ('document_id', 'storage_type', 'file_path', 'uploaded_at')
    search_fields = ('document_id', 'storage_type')
    list_filter = ('storage_type',)
