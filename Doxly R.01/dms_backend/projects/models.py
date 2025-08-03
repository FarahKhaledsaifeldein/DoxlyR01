from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError

User = get_user_model()

class Project(models.Model):
    name = models.CharField(max_length=255, unique=True)
    code = models.CharField(
        max_length=50,
        unique=True, 
        null=False,
        blank=False,
        validators=[RegexValidator(r'^[a-zA-Z0-9]+$', 'Only alphanumeric characters are allowed.')]
    )
    folder_path = models.CharField(max_length=500, blank=True, null=True)
    trade = models.CharField(max_length=100)
    sub_trade = models.CharField(max_length=100, blank=True, null=True)
    abbreviation = models.CharField(max_length=50, blank=True, null=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,  # Protect project if user is deleted
        null=True,       # Allows NULL in database (temporary)
        blank=True,      # Doesn't require form/API input
        editable=False   # Hides from admin/forms (auto-set only)
    )
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        if not self.pk and not self.created_by:
            from django.contrib.auth import get_user_model
            self.created_by = get_user_model().objects.get(id=1)   # New unsaved project?
        super().save(*args, **kwargs)
        if not self.folder_path:
            self.folder_path = f"/projects/{self.code}/"  # Or however you want to generate it
        super().save(*args, **kwargs)
              # Save again with folder path

    def __str__(self):
        return f"{self.name} ({self.code})"

    @classmethod
    def get_default_project(cls, user):
        """Gets or creates default project, FORCING the current user as creator"""
        try:
            # First try to get existing default project
            project = cls.objects.get(name="Default Project")
            return project
        except cls.DoesNotExist:
            # Create new default project with the user as creator
            return cls.objects.create(
                name="Default Project",
                description="Auto-created default project",
                created_by=user  # Force-set the creator
            )
        except Exception as e:
            raise ValidationError(f"Default project error: {str(e)}")

class FolderStructure(models.Model):
    """Model defining the folder structure for a project."""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="folders")
    name = models.CharField(max_length=255)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name="sub_folders")

    def __str__(self):
        return f"{self.project.name} - {self.name}"
