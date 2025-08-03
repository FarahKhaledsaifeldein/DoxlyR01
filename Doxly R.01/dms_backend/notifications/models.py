from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class EmailTemplate(models.Model):
    """Stores customizable email templates."""
    name = models.CharField(_('name'), max_length=255, unique=True)
    subject = models.CharField(_('subject'), max_length=255)
    body = models.TextField(_('body'))
    default_template = models.TextField(
        _('default template'),
        help_text=_("Stores the default template for reset purposes.")
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('email template')
        verbose_name_plural = _('email templates')
        ordering = ['name']

    def reset_to_default(self):
        """Resets the email body to the default template."""
        self.body = self.default_template
        self.save()

    def __str__(self):
        return self.name

class NotificationMail(models.Model):
    """Tracks notifications sent to users."""
    class Status(models.TextChoices):
        PENDING = 'pending', _('Pending')
        SENT = 'sent', _('Sent')
        FAILED = 'failed', _('Failed')
        DRAFT = 'draft', _('Draft')

    sender = models.ForeignKey(
        User,
        verbose_name=_('sender'),
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    
    recipient_email = models.EmailField(_('recipient email'))
    subject = models.CharField(_('subject'), max_length=255)
    body = models.TextField(_('body'))
    sent_at = models.DateTimeField(_('sent at'), auto_now_add=True)
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    is_read = models.BooleanField(_('is read'), default=False)

    class Meta:
        verbose_name = _('notification mail')
        verbose_name_plural = _('notifications mail')
        ordering = ['-sent_at']
        indexes = [
            models.Index(fields=['sender', 'recipient_email', 'is_read']),
            
            models.Index(fields=['status', 'sent_at']),
        ]

    def __str__(self):
        return f"{self.subject} - {self.status} (to {self.recipient_email})"