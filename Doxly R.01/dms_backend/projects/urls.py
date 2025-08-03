from django.urls import path
from .views import ProjectListCreateView, ProjectDetailView, FolderStructureListCreateView, FolderStructureDetailView

urlpatterns = [
    path('', ProjectListCreateView.as_view(), name='project-list'),
    path('<int:pk>/', ProjectDetailView.as_view(), name='project-detail'),
    path('folders/', FolderStructureListCreateView.as_view(), name='folder-list'),
    path('folders/<int:pk>/', FolderStructureDetailView.as_view(), name='folder-detail'),
]
