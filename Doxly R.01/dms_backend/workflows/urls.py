from django.urls import path
from .views import (
    WorkflowStageListCreateView, WorkflowStageDetailView,
    DocumentWorkflowListCreateView, DocumentWorkflowDetailView
)

urlpatterns = [
    path('stages/', WorkflowStageListCreateView.as_view(), name='workflow-stage-list'),
    path('stages/<int:pk>/', WorkflowStageDetailView.as_view(), name='workflow-stage-detail'),
    path('', DocumentWorkflowListCreateView.as_view(), name='document-workflow-list'),
    path('<int:pk>/', DocumentWorkflowDetailView.as_view(), name='document-workflow-detail'),
]
