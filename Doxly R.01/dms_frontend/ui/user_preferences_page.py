from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
                             QFormLayout, QLineEdit, QComboBox, QCheckBox, QTabWidget,
                             QFrame, QMessageBox, QGridLayout, QFileDialog)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QIcon
import os
import sys
import os

# Add the parent directory to sys.path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  
from utils.config_manager import ConfigManager

from PyQt6.QtCore import pyqtSignal

class UserPreferencesPage(QWidget):
    # Signal to notify when display name changes
    display_name_changed = pyqtSignal(str)
    
    def __init__(self, token=None, username=None):
        super().__init__()
        self.token = token
        self.username = username
        
        # Initialize config manager
        self.config_manager = ConfigManager(config_file="user_preferences.json")
        
        # Set default configuration values
        self.set_default_config()
        
        # Load saved configuration
        self.config = self.config_manager.load()
        
        self.setup_ui()
        
        # Apply loaded settings
        self.apply_settings()
    
    def setup_ui(self):
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Header
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 10)
        
        title = QLabel("User Preferences")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #ffffff;")
        header_layout.addWidget(title)
        
        save_btn = QPushButton("Save Changes")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        save_btn.clicked.connect(self.save_preferences)
        header_layout.addWidget(save_btn)
        
        main_layout.addWidget(header)
        
        # Create tabs for different preference categories
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                padding: 10px;
            }
            QTabBar::tab {
                background-color: #ecf0f1;
                color: #2c3e50;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            QTabBar::tab:selected {
                background-color: #3498db;
                color: white;
            }
        """)
        
        # Profile tab
        profile_tab = QWidget()
        profile_layout = QVBoxLayout(profile_tab)
        
        # Profile form
        profile_form = QWidget()
        form_layout = QFormLayout(profile_form)
        form_layout.setSpacing(15)
        form_layout.setContentsMargins(10, 10, 10, 10)
        
        # Profile picture
        profile_pic_widget = QWidget()
        profile_pic_layout = QHBoxLayout(profile_pic_widget)
        
        self.profile_pic = QLabel()
        self.profile_pic.setFixedSize(100, 100)
        self.profile_pic.setStyleSheet("""
            background-color: #3498db;
            border-radius: 50px;
            color: white;
            font-size: 36px;
            font-weight: bold;
        """)
        
        # Set initials
        if self.username:
            initials = self.username[0].upper() if self.username else "U"
            self.profile_pic.setText(initials)
            self.profile_pic.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        profile_pic_layout.addWidget(self.profile_pic)
        
        change_pic_btn = QPushButton("Change Picture")
        change_pic_btn.clicked.connect(self.change_profile_picture)
        profile_pic_layout.addWidget(change_pic_btn)
        profile_pic_layout.addStretch()
        
        # Form fields
        self.display_name = QLineEdit(self.username)
        self.email = QLineEdit("user@example.com")
        self.job_title = QLineEdit("Job Title")
        self.department = QLineEdit("Department")
        
        form_layout.addRow("Profile Picture:", profile_pic_widget)
        form_layout.addRow("Display Name:", self.display_name)
        form_layout.addRow("Email:", self.email)
        form_layout.addRow("Job Title:", self.job_title)
        form_layout.addRow("Department:", self.department)
        
        # Password change section
        password_section = QFrame()
        password_section.setFrameShape(QFrame.Shape.StyledPanel)
        password_section.setStyleSheet("""
            QFrame {
                background-color: #1e1f22;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        
        password_layout = QVBoxLayout(password_section)
        
        password_title = QLabel("Change Password")
        password_title.setStyleSheet("font-weight: bold; font-size: 16px;")
        password_layout.addWidget(password_title)
        
        password_form = QFormLayout()
        self.current_password = QLineEdit()
        self.current_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_password = QLineEdit()
        self.new_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password = QLineEdit()
        self.confirm_password.setEchoMode(QLineEdit.EchoMode.Password)
        
        password_form.addRow("Current Password:", self.current_password)
        password_form.addRow("New Password:", self.new_password)
        password_form.addRow("Confirm Password:", self.confirm_password)
        
        change_password_btn = QPushButton("Update Password")
        change_password_btn.clicked.connect(self.change_password)
        change_password_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        
        password_layout.addLayout(password_form)
        password_layout.addWidget(change_password_btn, alignment=Qt.AlignmentFlag.AlignRight)
        
        profile_layout.addWidget(profile_form)
        profile_layout.addWidget(password_section)
        profile_layout.addStretch()
        
        # Notifications tab
        notifications_tab = QWidget()
        notifications_layout = QVBoxLayout(notifications_tab)
        
        notifications_title = QLabel("Notification Settings")
        notifications_title.setStyleSheet("font-weight: bold; font-size: 16px;")
        notifications_layout.addWidget(notifications_title)
        
        # Email notifications
        email_notifications = QFrame()
        email_notifications.setFrameShape(QFrame.Shape.StyledPanel)
        email_notifications.setStyleSheet("""
            QFrame {
                background-color: #1e1f22;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        
        email_layout = QVBoxLayout(email_notifications)
        email_title = QLabel("Email Notifications")
        email_title.setStyleSheet("font-weight: bold;")
        email_layout.addWidget(email_title)
        
        self.notify_document_upload = QCheckBox("Document uploads")
        self.notify_document_upload.setChecked(True)
        self.notify_document_share = QCheckBox("Document shares")
        self.notify_document_share.setChecked(True)
        self.notify_comments = QCheckBox("Comments on documents")
        self.notify_comments.setChecked(True)
        self.notify_project_updates = QCheckBox("Project updates")
        self.notify_project_updates.setChecked(True)
        
        email_layout.addWidget(self.notify_document_upload)
        email_layout.addWidget(self.notify_document_share)
        email_layout.addWidget(self.notify_comments)
        email_layout.addWidget(self.notify_project_updates)
        
        notifications_layout.addWidget(email_notifications)
        notifications_layout.addStretch()
        
        # Add tabs
        tabs.addTab(profile_tab, "Profile")
        tabs.addTab(notifications_tab, "Notifications")
        
        main_layout.addWidget(tabs)
    
    def change_profile_picture(self):
        file_dialog = QFileDialog()
        file_dialog.setNameFilter("Images (*.png *.jpg *.jpeg)")
        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                # Here you would typically upload the image to server
                # and update the profile picture
                QMessageBox.information(self, "Profile Picture", "Profile picture updated successfully!")
    
    def change_password(self):
        if not self.current_password.text():
            QMessageBox.warning(self, "Error", "Please enter your current password")
            return
            
        if not self.new_password.text() or not self.confirm_password.text():
            QMessageBox.warning(self, "Error", "Please enter and confirm your new password")
            return
            
        if self.new_password.text() != self.confirm_password.text():
            QMessageBox.warning(self, "Error", "New passwords do not match")
            return
            
        # Here you would typically verify the current password and update to new password
        # For now, we'll just save the fact that the password was changed in our config
        self.config_manager.set("password_last_changed", "now")
        self.config_manager.save()
        
        QMessageBox.information(self, "Password", "Password updated successfully!")
        
        # Clear password fields
        self.current_password.clear()
        self.new_password.clear()
        self.confirm_password.clear()
    
    def set_default_config(self):
        """Set default configuration values"""
        defaults = {
            "profile": {
                "display_name": self.username or "",
                "email": "user@example.com",
                "job_title": "Job Title",
                "department": "Department"
            },
            "notifications": {
                "document_upload": True,
                "document_share": True,
                "comments": True,
                "project_updates": True
            }
        }
        
        self.config_manager.set_defaults(defaults)
    
    def apply_settings(self):
        """Apply loaded settings to UI components"""
        # Profile settings
        profile = self.config_manager.get("profile", {})
        self.display_name.setText(profile.get("display_name", self.username or ""))
        self.email.setText(profile.get("email", "user@example.com"))
        self.job_title.setText(profile.get("job_title", "Job Title"))
        self.department.setText(profile.get("department", "Department"))
        
        # Notification settings
        notifications = self.config_manager.get("notifications", {})
        self.notify_document_upload.setChecked(notifications.get("document_upload", True))
        self.notify_document_share.setChecked(notifications.get("document_share", True))
        self.notify_comments.setChecked(notifications.get("comments", True))
        self.notify_project_updates.setChecked(notifications.get("project_updates", True))
    
    def collect_settings(self):
        """Collect current settings from UI components"""
        settings = {
            "profile": {
                "display_name": self.display_name.text(),
                "email": self.email.text(),
                "job_title": self.job_title.text(),
                "department": self.department.text()
            },
            "notifications": {
                "document_upload": self.notify_document_upload.isChecked(),
                "document_share": self.notify_document_share.isChecked(),
                "comments": self.notify_comments.isChecked(),
                "project_updates": self.notify_project_updates.isChecked()
            }
        }
        
        return settings
    
    def save_preferences(self):
        """Save preferences to configuration file and apply them immediately"""
        # Get the current display name before saving
        old_display_name = self.config_manager.get("profile", {}).get("display_name", "")
        
        # Collect current settings
        settings = self.collect_settings()
        
        # Update config manager
        self.config_manager.update(settings)
        
        # Save to file
        if self.config_manager.save():
            # Apply the new settings immediately
            self.apply_settings()
            
            # Check if display name has changed
            new_display_name = settings["profile"]["display_name"]
            if new_display_name != old_display_name:
                # Emit signal with new display name
                self.display_name_changed.emit(new_display_name)
            
            QMessageBox.information(self, "Preferences", "Preferences saved and applied successfully!")
        else:
            QMessageBox.warning(self, "Preferences", "Failed to save preferences. Please try again.")