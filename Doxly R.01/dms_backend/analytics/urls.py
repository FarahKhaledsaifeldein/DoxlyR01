from django.urls import path
from .views import DocumentAnalysisListCreateView, analyze_document

urlpatterns = [
    path('analysis/', DocumentAnalysisListCreateView.as_view(), name='document-analysis-list'),
    path('analysis/run/', analyze_document, name='analyze-document'),
]
