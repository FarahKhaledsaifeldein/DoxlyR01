from django.urls import path
from .views import (
    EmailTemplateListCreateView, EmailTemplateDetailView,
    NotificationListView, send_email, reset_email_template,get_drafts,save_draft,get_emails
)

urlpatterns = [
    path('templates/', EmailTemplateListCreateView.as_view(), name='email-template-list'),
    path('templates/<int:pk>/', EmailTemplateDetailView.as_view(), name='email-template-detail'),
    path('templates/<int:pk>/reset/', reset_email_template, name='reset-email-template'),
    path('notifications/', NotificationListView.as_view(), name='notification-list'),
    path('email/send/', send_email, name='send-email'),
    path('emails/drafts/', get_drafts, name='get-drafts'),
    path('emails/', get_emails, name='get-emails'),
    path('emails/draft/save/', save_draft, name='save-draft'),

]
