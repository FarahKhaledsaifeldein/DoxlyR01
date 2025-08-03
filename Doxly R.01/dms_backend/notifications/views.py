from rest_framework import generics, permissions, filters, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from .models import EmailTemplate, NotificationMail
from .serializers import EmailTemplateSerializer, NotificationMailSerializer
from django.db.models import Q
from django.core.mail import EmailMessage
import logging
from django.core.exceptions import ValidationError
User = get_user_model()
logger = logging.getLogger(__name__)

# Email Template Views (unchanged)
class EmailTemplateListCreateView(generics.ListCreateAPIView):
    queryset = EmailTemplate.objects.all()
    serializer_class = EmailTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]

class EmailTemplateDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = EmailTemplate.objects.all()
    serializer_class = EmailTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]

@api_view(['POST'])
def reset_email_template(request, pk):
    try:
        template = EmailTemplate.objects.get(pk=pk)
        template.reset_to_default()
        return Response({"message": "Template reset to default successfully."})
    except EmailTemplate.DoesNotExist:
        return Response({"error": "Template not found."}, status=404)

# Notification/Email Views (updated)
class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationMailSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    ordering_fields = ['sent_at', 'status']
    ordering = ['-sent_at']

    def get_search_fields(self):
        if self.request.user.is_staff:
            return ['sender__username', 'sender__email', 'recipient_email', 'subject', 'body']
        return ['recipient_email', 'subject', 'body']

    def get_queryset(self):
        queryset = NotificationMail.objects.all()
        request = self.request
        
        # Filter by status if provided
        status_filter = request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status__iexact=status_filter)
        
        # Filter by read status if provided
        is_read = request.query_params.get('is_read')
        if is_read in ['true', 'false']:
            queryset = queryset.filter(is_read=is_read.lower() == 'true')
            
        # User isolation
        if not request.user.is_staff:
            queryset = queryset.filter(sender=request.user)
            
        # Search functionality
        search_term = request.query_params.get('search')
        if search_term:
            if request.user.is_staff:
                queryset = queryset.filter(
                    Q(sender__username__icontains=search_term) |
                    Q(sender__email__icontains=search_term) |
                    Q(recipient_email__icontains=search_term) |
                    Q(subject__icontains=search_term) |
                    Q(body__icontains=search_term)
                )
            else:
                queryset = queryset.filter(
                    Q(recipient_email__icontains=search_term) |
                    Q(subject__icontains=search_term) |
                    Q(body__icontains=search_term)
                )
        
        return queryset

class MarkAsReadView(generics.UpdateAPIView):
    queryset = NotificationMail.objects.all()
    serializer_class = NotificationMailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        mail = self.get_object()
        mail.is_read = True
        mail.save()
        return Response({'status': 'marked as read'})

@api_view(['POST'])
def send_email(request):
    """API to send email notifications with optional file attachments."""
    sender = request.user
    recipient = request.data.get("recipient_email")
    subject = request.data.get("subject")
    body = request.data.get("body")
    attachments = request.FILES.getlist("attachments")
    sent_at = request.data.get("sent_at")

    if not recipient or not subject or not body:
        return Response({"error": "Missing required fields."}, status=400)

    try:
        email = EmailMessage(
            subject=subject,
            body=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            
            to=[recipient]
        )

        # Handle attachments
        for attachment in attachments:
            email.attach(attachment.name, attachment.read(), attachment.content_type)

        # Send email and record with 'sent' status
        email.send()
        
        NotificationMail.objects.create(
            sender=sender,
            recipient_email=recipient,
            subject=subject,
            body=body,
            
            status="sent",
            
        )
        return Response({"message": "Email sent successfully.",
        "sent_at": sent_at
        })
    except Exception as e:
        # Record failed attempt
        NotificationMail.objects.create(
            sender=sender,
            recipient_email=recipient,
            subject=subject,
            body=body,
            
            status="failed",
            
        )
        return Response({"error": f"Failed to send email: {str(e)}"}, status=500)

@api_view(['GET'])
def get_emails(request):
    """Get all emails (sent, received, etc.) excluding drafts"""
    user = request.user
    
    if user.is_staff:
        emails = NotificationMail.objects.exclude(status='draft').order_by('-sent_at')
    else:
        emails = NotificationMail.objects.filter(sender=user).exclude(status='draft').order_by('-sent_at')
    
    serializer = NotificationMailSerializer(emails, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def save_draft(request):
    """API to send email notifications with optional file attachments."""
    sender = request.user
    recipient = request.data.get("recipient_email")
    subject = request.data.get("subject")
    body = request.data.get("body")
    attachments = request.FILES.getlist("attachments")
    sent_at = request.data.get("sent_at")

    

    try:
        email = NotificationMail.objects.create(
            sender=sender,
            recipient_email=recipient,
            subject=subject,
            body=body,
            
            status="draft")

        # Handle attachments
        for attachment in attachments:
            email.attach(attachment.name, attachment.read(), attachment.content_type)
            email.save()
        
        return Response({
            "message": "Draft saved successfully",
            "draft_id": email.id,
            "sent_at": sent_at
        }, status=status.HTTP_201_CREATED)

        
    except ValidationError as ve:
        logger.error({f"Draft save failed:{ve.message_dict} "},status=400)
        return Response(
            {"error": f"Failed to save draft: {str(ve)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def get_drafts(request):
    """Get only draft emails for the current user"""
    drafts = NotificationMail.objects.filter(
        sender=request.user,
        status="draft"
    ).order_by('-sent_at')
    
    serializer = NotificationMailSerializer(drafts, many=True)
    return Response(serializer.data)
'''from rest_framework import generics, permissions, filters, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from .models import EmailTemplate, NotificationMail
from .serializers import EmailTemplateSerializer, NotificationMailSerializer
from django.db.models import Q
from django.core.mail import EmailMessage
User = get_user_model()
class EmailTemplateListCreateView(generics.ListCreateAPIView):
    """View for listing and creating email templates."""
    queryset = EmailTemplate.objects.all()
    serializer_class = EmailTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]

class EmailTemplateDetailView(generics.RetrieveUpdateDestroyAPIView):
    """View for retrieving, updating, and deleting email templates."""
    queryset = EmailTemplate.objects.all()
    serializer_class = EmailTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]

@api_view(['POST'])
def reset_email_template(request, pk):
    """API endpoint to reset an email template to its default version."""
    try:
        template = EmailTemplate.objects.get(pk=pk)
        template.reset_to_default()
        return Response({"message": "Template reset to default successfully."})
    except EmailTemplate.DoesNotExist:
        return Response({"error": "Template not found."}, status=404)


class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationMailSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    # Step 1: Configure filters
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    ordering_fields = ['sent_at', 'status']
    ordering = ['-sent_at']  # Default ordering

    # Step 2: Separate search fields for admin vs regular users
    def get_search_fields(self):
        if self.request.user.is_staff:
            return ['sender__username', 'sender__email', 'recipient_email', 'subject', 'body']
        return ['recipient_email', 'subject', 'body']  # Regular users only search notification content

    # Step 3: Enhanced get_queryset
    def get_queryset(self):
        queryset = NotificationMail.objects.all()
        request = self.request
        is_read = request.query_params.get('is_read')
        search_term = request.query_params.get('search')
        user_id = request.query_params.get('user_id')

        # Step 4: Strict user isolation
        if not request.user.is_staff:
            queryset = queryset.filter(sender=request.user)
            
            # Regular users can only search their own notifications
            if search_term:
                queryset = queryset.filter(
                    Q(recipient_email__icontains=search_term) |
                    Q(subject__icontains=search_term) |
                    Q(body__icontains=search_term)
                )
        else:
            # Admin-specific filters
            if user_id:
                try:
                    sender = User.objects.get(pk=user_id)
                    queryset = queryset.filter(sender=sender)
                except User.DoesNotExist:
                    return NotificationMail.objects.none()

            # Admin search covers both user and notification fields
            if search_term:
                queryset = queryset.filter(
                    Q(sender__username__icontains=search_term) |
                    Q(sender__email__icontains=search_term) |
                    Q(recipient_email__icontains=search_term) |
                    Q(subject__icontains=search_term) |
                    Q(body__icontains=search_term)
                )

        # Common filter
        if is_read in ['true', 'false']:
            queryset = queryset.filter(is_read=is_read.lower() == 'true')
            
        return queryset
class MarkAsReadView(generics.UpdateAPIView):
    queryset = NotificationMail.objects.all()
    serializer_class = NotificationMailSerializer

    def update(self, request, *args, **kwargs):
        mail = self.get_object()
        mail.is_read = True  # Mark as read
        mail.save()
        return Response({'status': 'marked as read'})


@api_view(['POST'])
def send_email(request):


    """API to send email notifications with optional file attachments."""
    sender=request.user
    recipient = request.data.get("recipient_email")
    subject = request.data.get("subject")
    body = request.data.get("body")
    attachments = request.FILES.getlist("attachments")

    if not recipient or not subject or not body:
        return Response({"error": "Missing required fields."}, status=400)

    try:
        email = EmailMessage(
           # user=sender,
            subject=subject,
            body=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient]
        )

        # Handle attachments if present
        for attachment in attachments:
            email.attach(attachment.name, attachment.read(), attachment.content_type)

        email.send()

        NotificationMail.objects.create(
            sender=request.user,
            recipient_email=recipient,
            subject=subject,
            body=body,
            status="sent"
        )
        return Response({"message": "Email sent successfully."})
    except Exception as e:
        NotificationMail.objects.create(
            sender=request.user,
            recipient_email=recipient,
            subject=subject,
            body=body,
            status="failed"
        )
        return Response({"error": f"Failed to send email: {str(e)}"}, status=500)
@api_view(['GET'])
def get_emails(request):
    """
    API endpoint to get all emails (with optional filtering).
    For non-staff users, only returns their own emails.
    """
    user = request.user
    
    if user.is_staff:
        emails = NotificationMail.objects.all().order_by('-sent_at')
    else:
        emails = NotificationMail.objects.filter(sender=user).order_by('-sent_at')
    
    serializer = NotificationMailSerializer(emails, many=True)
    return Response(serializer.data)
       # In your views.py
@api_view(['POST'])
def save_draft(request):
    """API to save email drafts."""
    try:
        draft_data = {
            'sender': request.user.id,
            'recipient_email': request.data.get("recipient_email", ""),
            'subject': request.data.get("subject", ""),
            'body': request.data.get("body", ""),
            'cc': request.data.get("cc", ""),
            'bcc': request.data.get("bcc", ""),
            'status': "draft"
        }
        
        # Handle attachments if any
        attachments = request.FILES.getlist('attachments', [])
        
        # Create the draft
        draft = NotificationMail.objects.create(**draft_data)
        
        # If you have attachment handling, process them here
        
        return Response({"message": "Draft saved successfully."}, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Failed to save draft: {str(e)}")
        return Response({"error": f"Failed to save draft: {str(e)}"}, 
                       status=status.HTTP_500_INTERNAL_SERVER_ERROR)
@api_view(['GET'])
def get_drafts(request):
    """API to retrieve saved drafts."""
    drafts = NotificationMail.objects.filter(
        sender=request.user,
        status="draft"
    ).order_by('-sent_at')
    
    serializer = NotificationMailSerializer(drafts, many=True)
    return Response(serializer.data)'''