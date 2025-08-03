from django.db import models
from django.contrib.auth import get_user_model
from projects.models import Project
import uuid
from datetime import timedelta
from django.utils import timezone
import os
from cryptography.fernet import Fernet
from django.conf import settings
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

User = get_user_model()
def get_document_upload_path(instance, filename):
    """
    Returns upload path like: 'documents/projects/{project_id}/{year}/{month}/{filename}'
    - instance: The Document model instance
    - filename: Original filename of uploaded file
    """
    now = timezone.now()
    return os.path.join(
        'documents',
        'projects',
        str(instance.project.id),  # Organize by project
        str(now.year),            # Then by year
        str(now.month),           # Then by month
        filename                  # Original filename
    )
class Document(models.Model):
    """Enhanced document model with complete tracking"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="documents",null=True,blank=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    reference_code = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    file = models.FileField(upload_to=get_document_upload_path)  # Custom upload path
    file_name = models.CharField(max_length=255, blank=True)  # New field for searchable filename

    # Add this method to auto-save the filename
    def save(self, *args, **kwargs):
        if self.file:  # Only update if file exists
            self.file_name = self.file.name.split("/")[-1]  # Extracts "report.pdf"
        super().save(*args, **kwargs)  # Call the parent save()

    def __str__(self):
        return self.name
    file_size = models.BigIntegerField(default=0)
    file_type = models.CharField(max_length=50, blank=True)
    version = models.PositiveIntegerField(default=1)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="uploaded_documents")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    is_encrypted = models.BooleanField(default=False)
    encryption_key = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, default='draft',
                            choices=[
                                ('draft', 'Draft'),
                                ('active', 'Active'),
                                ('archived', 'Archived')
                            ])
    is_shared = models.BooleanField(default=False)
    doc_id = models.CharField(
        max_length=50,
        unique=True,
        editable=False,
        default=uuid.uuid4
    )

    class Meta:
        ordering = ['-uploaded_at']
        permissions = [
            ('share_document', 'Can share document'),
            ('download_document', 'Can download document'),
        ]

    def __str__(self):
        return f"{self.name} (v{self.version})"

    def save(self, *args, **kwargs):
        """Custom save with file processing"""
        if not self.pk and self.file:  # New document
            self.process_new_document()
        super().save(*args, **kwargs)
        if not self.project:
            self.project = Project.get_default_project()

        if not self.doc_id:
            year = timezone.now().strftime('%Y')
            last_doc = Document.objects.filter(doc_id__startswith=f"DOC-{year}-").order_by('doc_id').last()
            seq = int(last_doc.doc_id.split('-')[-1]) + 1 if last_doc else 1
            self.doc_id = f"DOC-{year}-{seq:04d}"

        super().save(*args, **kwargs)

    def process_new_document(self):
        """Handle new document processing"""
        self.file_size = self.file.size
        self.file_type = os.path.splitext(self.file.name)[1][1:].lower()
        
        if self.is_encrypted:
            self.encrypt_document()

    def get_absolute_path(self):
        """Get full filesystem path"""
        return os.path.join(settings.MEDIA_ROOT, self.file.name)

    def get_download_url(self):
        """Get download URL"""
        return settings.MEDIA_URL + self.file.name

    def encrypt_document(self):
        """Implement AES-256 encryption logic."""
        if not self.file:
            return
        
        key = self.generate_key()
        f = Fernet(key)
        
        # Read the file content
        self.file.seek(0)
        file_data = self.file.read()
        
        # Encrypt the content
        encrypted_data = f.encrypt(file_data)
        
        # Create a temporary file with encrypted content
        temp_path = f"{self.file.path}.encrypted"
        with open(temp_path, 'wb') as encrypted_file:
            encrypted_file.write(encrypted_data)
            
        # Replace the original file with encrypted one
        os.replace(temp_path, self.file.path)

    def generate_document_code(self, b, c, d, e, f, g, h_number):
        """Generate a formatted document code."""
        return f"{b}-{c}-{d}-{e}-{f}-{g}-{int(h_number):06}"

    def is_latest_revision(self):
        """Check if the document is at its latest revision."""
        latest = self.versions.order_by('-uploaded_at').first()
        return latest and latest.version == self.version

    def is_latest_drawing(self, drawing_code, rev_num, drawing_list):
        """Validate if the drawing is at its latest revision."""
        max_rev = max((d.rev for d in drawing_list if d.code == drawing_code), default=None)
        return rev_num == max_rev

    def get_references_for_document(self, all_docs):
        """Get reference IDs from related documents."""
        code = f"{self.reference_code}_R{self.version}"
        return [
            f"{d.reference_code}_R{d.version}"
            for d in all_docs if code in getattr(d, 'references', [])
        ]

    def get_reference_dates(self, all_docs):
        """Get formatted dates of referenced documents."""
        related_dates = []
        for d in all_docs:
            if str(self.reference_code) in getattr(d, 'references', []):
                related_dates.append(d.uploaded_at.strftime('%d/%m/%Y'))
        return ', '.join(set(related_dates))

    def calculate_due_date(self, start_date, days, holidays, weekends=(5, 6)):
        """Calculate due date considering holidays and weekends."""
        date = start_date
        count = 0
        while count < days:
            date += timedelta(days=1)
            if date.weekday() not in weekends and date not in holidays:
                count += 1
        return date

    def count_vacation_overlap(self, start, end, vacations):
        """Calculate overlap with vacation periods."""
        days = 0
        for vac in vacations:
            if vac.end_date >= start and vac.start_date <= end:
                overlap_start = max(start, vac.start_date)
                overlap_end = min(end, vac.end_date)
                days += (overlap_end - overlap_start).days + 1
        return days

    def determine_document_status(self):
        """Determine document status based on various conditions."""
        if not hasattr(self, 'status'):
            return "Status code is empty"
        
        status_code = getattr(self.status, 'code', '')
        if status_code == "URE":
            return "URE"
        if status_code in ["A", "B", "D", "E"]:
            return "Closed"
        if status_code == "C":
            return "Open need Revision" if not self.is_latest_revision() else "Closed"
        return "Status code is empty"

    def get_final_close_date(self):
        """Get the final closing date of the document."""
        dates = [
            getattr(self, 'completed_date', None),
            getattr(self, 'due_date', None),
            self.uploaded_at
        ]
        return max(filter(None, dates), default=None)

    def build_document_folder_path(self, project_name, sender):
        """Build the folder path for document storage."""
        return os.path.join(
            "doxly", "projects", project_name.replace(" ", "_"),
            f"{self.reference_code}_R{self.version}", sender
        )

    def check_document_files(self, base_path):
        """Check existence of document files in different formats."""
        result = {}
        for ext in ["pdf", "docx", "xlsx"]:
            full_path = os.path.join(
                base_path, 
                f"{self.reference_code}_R{self.version}.{ext}"
            )
            result[ext] = os.path.exists(full_path)
        return result

    def get_overdue_days(self):
        """Calculate number of overdue days."""
        if hasattr(self, 'due_date') and not hasattr(self, 'completed_date'):
            delta = (timezone.now() - self.due_date).days
            return max(delta, 0)
        return 0

    def get_delay_status(self):
        """Determine delay status of the document."""
        if not hasattr(self, 'completed_date') and hasattr(self, 'due_date'):
            return "Overdue" if timezone.now().date() > self.due_date.date() else "URE"
        if hasattr(self, 'completed_date') and self.completed_date > self.due_date:
            return "Delay"
        return "On Date"

class DocumentVersion(models.Model):
    """Model for tracking document versions."""
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name="versions")
    version = models.PositiveIntegerField()
    file = models.FileField(upload_to='documents/versions/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('document', 'version')

    def __str__(self):
        return f"{self.document.name} - v{self.version}"

    def generate_key(self):
        """Generate an encryption key using PBKDF2."""
        salt = base64.b64decode(settings.ENCRYPTION_SALT)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.b64encode(kdf.derive(settings.SECRET_KEY.encode()))
        return key

    def decrypt_document(self):
        """Decrypt the document using AES-256."""
        if not self.file or not self.is_encrypted:
            return None
            
        key = self.generate_key()
        f = Fernet(key)
        
        # Read the encrypted content
        self.file.seek(0)
        encrypted_data = self.file.read()
        
        # Decrypt the content
        try:
            decrypted_data = f.decrypt(encrypted_data)
            return decrypted_data
        except Exception as e:
            raise ValueError(f"Decryption failed: {str(e)}")

class DocumentShare(models.Model):
    """Model for tracking document sharing"""
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='shares')
    shared_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shared_documents')
    shared_with = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shared_with_me')
    shared_at = models.DateTimeField(auto_now_add=True)
    permission_level = models.CharField(max_length=20,
                                       choices=[
                                           ('view', 'Can View'),
                                           ('edit', 'Can Edit'),
                                           ('download', 'Can Download')
                                       ],
                                       default='view')
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('document', 'shared_with')
        ordering = ['-shared_at']

    def __str__(self):
        return f"{self.document.name} shared with {self.shared_with.email}"

