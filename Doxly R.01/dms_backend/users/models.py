from django.contrib.auth.models import AbstractUser
from django.db import models

# Define user roles
USER_ROLES = (
    ('admin', 'Admin'),
    ('manager', 'Manager'),
    ('editor', 'Editor'),
    ('viewer', 'Viewer'),
)

class CustomUser(AbstractUser):
    """
    Custom user model extending Django's AbstractUser.
    Adds roles for access control.
    """
    role = models.CharField(max_length=20, choices=USER_ROLES, default='viewer')

    def __str__(self):
        return f"{self.username} ({self.role})"
'''from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        
        # Generate a username if not provided
        if not extra_fields.get("username"):
            extra_fields["username"] = email.split("@")[0]
        
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True, blank=True, null=True)
    role = models.CharField(max_length=50, choices=[("admin", "Admin"), ("manager", "Manager"), ("user", "User")], default="user")

    objects = CustomUserManager()

    USERNAME_FIELD = "email"  # Login with email
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

'''