from django.contrib import admin
from .models import DocumentAnalysis

@admin.register(DocumentAnalysis)
class DocumentAnalysisAdmin(admin.ModelAdmin):
    list_display = ('document_id', 'classification', 'predicted_due_date', 'created_at')
    search_fields = ('document_id', 'classification')
    list_filter = ('classification', 'predicted_due_date')
