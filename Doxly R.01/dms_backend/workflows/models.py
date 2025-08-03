from django.db import models
from django.contrib.auth import get_user_model
from documents.models import Document

User = get_user_model()

class WorkflowStage(models.Model):
    """Represents a stage in a document approval workflow."""
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    sequence = models.PositiveIntegerField(help_text="Defines the order of stages.")
    requires_approval = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.sequence}: {self.name}"

class DocumentWorkflow(models.Model):
    """Tracks the workflow of a document, linking it to various approval stages."""
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name="workflows")
    current_stage = models.ForeignKey(WorkflowStage, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')],
        default='pending'
    )
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="workflow_assigned")
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="workflow_reviewed")
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.document.name} - {self.current_stage.name if self.current_stage else 'Not Assigned'} - {self.status}"
