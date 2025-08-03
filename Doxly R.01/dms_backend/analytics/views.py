from rest_framework import generics, permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
import random
import datetime
from .models import DocumentAnalysis
from .serializers import DocumentAnalysisSerializer

# Simulating AI-based classification and anomaly detection
def ai_classify_document():
    """Simulate AI-based document classification."""
    categories = ["Technical Report", "Legal Contract", "Financial Statement", "Blueprint", "Specification"]
    return random.choice(categories)

def ai_predict_due_date():
    """Simulate AI-based due date prediction."""
    today = datetime.date.today()
    return today + datetime.timedelta(days=random.randint(10, 60))

def ai_detect_anomalies():
    """Simulate AI-based anomaly detection in documents."""
    anomalies = ["Missing signature", "Duplicate entries", "Unexpected content", "Incomplete data"]
    return ", ".join(random.sample(anomalies, k=random.randint(0, 2))) if random.random() > 0.5 else "No anomalies"

class DocumentAnalysisListCreateView(generics.ListCreateAPIView):
    """API to retrieve and store AI analysis results."""
    queryset = DocumentAnalysis.objects.all()
    serializer_class = DocumentAnalysisSerializer
    permission_classes = [permissions.IsAuthenticated]

@api_view(['POST'])
def analyze_document(request):
    """Endpoint to perform AI-based document analysis."""
    document_id = request.data.get("document_id")

    if not document_id:
        return Response({"error": "Document ID is required"}, status=400)

    analysis = DocumentAnalysis.objects.create(
        document_id=document_id,
        classification=ai_classify_document(),
        predicted_due_date=ai_predict_due_date(),
        anomalies_detected=ai_detect_anomalies()
    )

    serializer = DocumentAnalysisSerializer(analysis)
    return Response(serializer.data)
