import os
import subprocess
from PyQt6.QtWidgets import QMessageBox

class OfficeHandler:
    def __init__(self, parent=None):
        self.parent = parent
        self.office_apps = {
            'word': {
                'exe': 'WINWORD.EXE',
                'extensions': ['.doc', '.docx', '.rtf'],
                'name': 'Microsoft Word'
            },
            'excel': {
                'exe': 'EXCEL.EXE',
                'extensions': ['.xls', '.xlsx', '.csv'],
                'name': 'Microsoft Excel'
            },
            'outlook': {
                'exe': 'OUTLOOK.EXE',
                'extensions': [],
                'name': 'Microsoft Outlook'
            }
        }

    def check_office_app(self, app_name):
        """Check if an Office application is installed"""
        try:
            # Check common installation paths for Office applications
            program_files_paths = [
                os.path.join(os.environ.get('ProgramFiles', ''), 'Microsoft Office', 'root', 'Office16'),
                os.path.join(os.environ.get('ProgramFiles(x86)', ''), 'Microsoft Office', 'root', 'Office16'),
                os.path.join(os.environ.get('ProgramFiles', ''), 'Microsoft Office\\Office16'),
                os.path.join(os.environ.get('ProgramFiles(x86)', ''), 'Microsoft Office\\Office16')
            ]
            
            app_info = self.office_apps.get(app_name.lower())
            if not app_info:
                return False, None
            
            for path in program_files_paths:
                if os.path.exists(os.path.join(path, app_info['exe'])):
                    return True, os.path.join(path, app_info['exe'])
            
            return False, None
        except Exception as e:
            return False, str(e)

    def get_app_for_file(self, file_path):
        """Determine which Office application should handle the file based on extension"""
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        for app_name, app_info in self.office_apps.items():
            if ext in app_info['extensions']:
                return app_name
        return None

    def open_document(self, file_path):
        """Open a document with the appropriate Office application"""
        try:
            app_name = self.get_app_for_file(file_path)
            if not app_name:
                QMessageBox.warning(
                    self.parent,
                    "Unsupported File Type",
                    "This file type is not supported for direct opening."
                )
                return False

            app_available, app_path = self.check_office_app(app_name)
            if not app_available:
                QMessageBox.warning(
                    self.parent,
                    "Application Not Found",
                    f"{self.office_apps[app_name]['name']} is not installed on your system. "
                    "Please install Microsoft Office to open this type of file."
                )
                return False

            try:
                subprocess.Popen([app_path, file_path])
                return True
            except Exception as e:
                QMessageBox.warning(
                    self.parent,
                    "Error",
                    f"Could not open file with {self.office_apps[app_name]['name']}: {str(e)}\n\n"
                    f"Please make sure {self.office_apps[app_name]['name']} is properly installed and configured."
                )
                return False

        except Exception as e:
            QMessageBox.critical(
                self.parent,
                "Error",
                f"An unexpected error occurred while opening the file: {str(e)}"
            )
            return False