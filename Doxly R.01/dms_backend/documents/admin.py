from django.contrib import admin
from .models import Document, DocumentVersion

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'project', 'version', 'uploaded_by', 'uploaded_at', 'is_encrypted')
    search_fields = ('name', 'project__name')
    list_filter = ('uploaded_by', 'project')

@admin.register(DocumentVersion)
class DocumentVersionAdmin(admin.ModelAdmin):
    list_display = ('id', 'document', 'version', 'uploaded_at')
    search_fields = ('document__name',)
