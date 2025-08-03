from django.contrib import admin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    """
    Admin configuration for the CustomUser model.
    Allows filtering by role.
    """
    list_display = ('username', 'email', 'role')
    list_filter = ('role',)

'''from django.contrib import admin
from django.contrib.auth import get_user_model

User = get_user_model()

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "username", "role", "is_staff", "is_active")
    search_fields = ("email", "username")'''
