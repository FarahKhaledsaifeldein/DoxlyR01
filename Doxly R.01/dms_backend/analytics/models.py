from django.db import models

class DocumentAnalysis(models.Model):
    """Stores AI analysis results for documents."""
    document_id = models.UUIDField(unique=True)
    classification = models.CharField(max_length=255, null=True, blank=True)
    predicted_due_date = models.DateField(null=True, blank=True)
    anomalies_detected = models.TextField(null=True, blank=True)  # Stores anomaly details
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Analysis for Document {self.document_id}"
