from django.contrib import admin
from .models import Project, FolderStructure

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user  # Auto-set admin as creator
        super().save_model(request, obj, form, change)
    list_display = ('id', 'name', 'code',  'created_by', 'created_at')#'server_name',
    search_fields = ('name', 'code')
    list_filter = ('created_by',)

    # admin.py


@admin.register(FolderStructure)
class FolderStructureAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'project', 'parent')
    search_fields = ('name', 'project__name')
