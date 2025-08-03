from rest_framework import generics, permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import StorageLocation
from .serializers import StorageLocationSerializer
import os

class StorageListCreateView(generics.ListCreateAPIView):
    """API to manage document storage records."""
    queryset = StorageLocation.objects.all()
    serializer_class = StorageLocationSerializer
    permission_classes = [permissions.IsAuthenticated]

@api_view(['POST'])
def upload_document(request):
    """Upload a document to a chosen storage type."""
    document_id = request.data.get("document_id")
    file = request.FILES.get("file")
    storage_type = request.data.get("storage_type", "local")

    if not document_id or not file:
        return Response({"error": "Document ID and file are required"}, status=400)

    file_path = f"storage/{document_id}/{file.name}"

    if storage_type == "local":
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as f:
            for chunk in file.chunks():
                f.write(chunk)

    storage_record = StorageLocation.objects.create(
        document_id=document_id,
        storage_type=storage_type,
        file_path=file_path
    )

    serializer = StorageLocationSerializer(storage_record)
    return Response(serializer.data)
