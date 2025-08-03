from django.contrib import admin
from .models import WorkflowStage, DocumentWorkflow

@admin.register(WorkflowStage)
class WorkflowStageAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'sequence', 'requires_approval')
    search_fields = ('name',)
    list_filter = ('requires_approval',)

@admin.register(DocumentWorkflow)
class DocumentWorkflowAdmin(admin.ModelAdmin):
    list_display = ('id', 'document', 'current_stage', 'status', 'assigned_to', 'last_updated')
    search_fields = ('document__name',)
    list_filter = ('status',)
