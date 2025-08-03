"""
URL configuration for dms_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse

def home(request):
    return HttpResponse("It Worked!")



urlpatterns = [
     path('', home, name='home'), # this will match the root url
    path('admin/', admin.site.urls),  # Admin Panel
    path('api/users/', include('users.urls')),  # User Management
    path('api/projects/', include('projects.urls')),  # Project Management
    path('api/documents/', include('documents.urls')),  # Document Management
    path('api/workflows/', include('workflows.urls')),  # Workflows
    path('api/notifications/', include('notifications.urls')),  # Notifications
    path('api/analytics/', include('analytics.urls')),  # AI/ML Analytics
    path('api/storage/', include('storage.urls')),  # Cloud/Local Storage

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
