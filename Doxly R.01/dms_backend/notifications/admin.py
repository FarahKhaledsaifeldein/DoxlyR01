from django.contrib import admin
from .models import EmailTemplate, NotificationMail
@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'subject', 'updated_at')
    search_fields = ('name', 'subject')
    list_filter = ('updated_at',)

@admin.register(NotificationMail)
class NotificationMailAdmin(admin.ModelAdmin):
    list_display = ('id','sender','recipient_email','subject', 'status', 'sent_at','is_read')
    search_fields = ('sender__username','sender__email','recipient_email', 'subject')
    list_filter = ('status','sent_at','is_read')
    def sender_email(self, obj):
        return obj.sender.email
    sender_email.short_description = 'Sender Email'