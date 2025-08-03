from django.urls import path
from .views import StorageListCreateView, upload_document

urlpatterns = [
    path('storage/', StorageListCreateView.as_view(), name='storage-list'),
    path('storage/upload/', upload_document, name='upload-document'),
]
