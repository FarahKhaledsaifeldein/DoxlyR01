from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
                             QFormLayout, QLineEdit, QComboBox, QCheckBox, QTabWidget,
                             QFrame, QMessageBox, QGridLayout, QSlider, QColorDialog,
                             QFontDialog, QFileDialog, QGroupBox, QRadioButton, QSpinBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
import os

import sys
import os

# Add the parent directory to sys.path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  
from utils.config_manager import ConfigManager

class SettingsPage(QWidget):
    def __init__(self, token=None, username=None):
        super().__init__()
        self.token = token
        self.username = username
        
        # Initialize config manager
        self.config_manager = ConfigManager()
        
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
        
        title = QLabel("Settings")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        header_layout.addWidget(title)
        
        save_btn = QPushButton("Save Settings")
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
        save_btn.clicked.connect(self.save_settings)
        header_layout.addWidget(save_btn)
        
        reset_btn = QPushButton("Reset to Default")
        reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        reset_btn.clicked.connect(self.reset_settings)
        header_layout.addWidget(reset_btn)
        
        main_layout.addWidget(header)
        
        # Create tabs for different settings categories
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
        
        # General settings tab
        general_tab = QWidget()
        general_layout = QVBoxLayout(general_tab)
        
        # Application settings
        app_settings = QGroupBox("Application Settings")
        app_settings_layout = QFormLayout(app_settings)
        
        self.language_combo = QComboBox()
        self.language_combo.addItems(["English", "Spanish", "French", "German", "Chinese"])
        app_settings_layout.addRow("Language:", self.language_combo)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark", "System Default"])
        app_settings_layout.addRow("Theme:", self.theme_combo)
        
        self.startup_check = QCheckBox("Launch on system startup")
        app_settings_layout.addRow("", self.startup_check)
        
        self.update_check = QCheckBox("Check for updates automatically")
        self.update_check.setChecked(True)
        app_settings_layout.addRow("", self.update_check)
        
        general_layout.addWidget(app_settings)
        
        # File handling settings
        file_settings = QGroupBox("File Handling")
        file_settings_layout = QFormLayout(file_settings)
        
        self.default_location = QLineEdit("C:/Users/Documents/Doxly")
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_location)
        
        location_widget = QWidget()
        location_layout = QHBoxLayout(location_widget)
        location_layout.setContentsMargins(0, 0, 0, 0)
        location_layout.addWidget(self.default_location)
        location_layout.addWidget(browse_btn)
        
        file_settings_layout.addRow("Default save location:", location_widget)
        
        self.file_format_combo = QComboBox()
        self.file_format_combo.addItems(["PDF", "DOCX", "XLSX", "CSV", "TXT"])
        file_settings_layout.addRow("Default export format:", self.file_format_combo)
        
        self.compress_check = QCheckBox("Compress files when uploading")
        self.compress_check.setChecked(True)
        file_settings_layout.addRow("", self.compress_check)
        
        general_layout.addWidget(file_settings)
        general_layout.addStretch()
        
        # Display settings tab
        display_tab = QWidget()
        display_layout = QVBoxLayout(display_tab)
        
        # Font settings
        font_settings = QGroupBox("Font Settings")
        font_settings_layout = QFormLayout(font_settings)
        
        self.font_label = QLabel("Arial, 12pt")
        font_btn = QPushButton("Change Font...")
        font_btn.clicked.connect(self.change_font)
        
        font_widget = QWidget()
        font_layout = QHBoxLayout(font_widget)
        font_layout.setContentsMargins(0, 0, 0, 0)
        font_layout.addWidget(self.font_label)
        font_layout.addWidget(font_btn)
        
        font_settings_layout.addRow("Application font:", font_widget)
        
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 24)
        self.font_size_spin.setValue(12)
        font_settings_layout.addRow("Default font size:", self.font_size_spin)
        
        display_layout.addWidget(font_settings)
        
        # Color settings
        color_settings = QGroupBox("Color Settings")
        color_settings_layout = QGridLayout(color_settings)
        
        # Primary color
        self.primary_color = QColor("#3498db")
        self.primary_color_btn = QPushButton()
        self.primary_color_btn.setStyleSheet(f"background-color: {self.primary_color.name()};")
        self.primary_color_btn.setFixedSize(30, 30)
        self.primary_color_btn.clicked.connect(lambda: self.change_color("primary"))
        color_settings_layout.addWidget(QLabel("Primary Color:"), 0, 0)
        color_settings_layout.addWidget(self.primary_color_btn, 0, 1)
        
        # Secondary color
        self.secondary_color = QColor("#2ecc71")
        self.secondary_color_btn = QPushButton()
        self.secondary_color_btn.setStyleSheet(f"background-color: {self.secondary_color.name()};")
        self.secondary_color_btn.setFixedSize(30, 30)
        self.secondary_color_btn.clicked.connect(lambda: self.change_color("secondary"))
        color_settings_layout.addWidget(QLabel("Secondary Color:"), 1, 0)
        color_settings_layout.addWidget(self.secondary_color_btn, 1, 1)
        
        # Accent color
        self.accent_color = QColor("#e74c3c")
        self.accent_color_btn = QPushButton()
        self.accent_color_btn.setStyleSheet(f"background-color: {self.accent_color.name()};")
        self.accent_color_btn.setFixedSize(30, 30)
        self.accent_color_btn.clicked.connect(lambda: self.change_color("accent"))
        color_settings_layout.addWidget(QLabel("Accent Color:"), 2, 0)
        color_settings_layout.addWidget(self.accent_color_btn, 2, 1)
        
        # Reset colors button
        reset_colors_btn = QPushButton("Reset Colors")
        reset_colors_btn.clicked.connect(self.reset_colors)
        color_settings_layout.addWidget(reset_colors_btn, 3, 0, 1, 2)
        
        display_layout.addWidget(color_settings)
        
        # Layout settings
        layout_settings = QGroupBox("Layout Settings")
        layout_settings_layout = QFormLayout(layout_settings)
        
        self.sidebar_check = QCheckBox("Show sidebar")
        self.sidebar_check.setChecked(True)
        layout_settings_layout.addRow("", self.sidebar_check)
        
        self.toolbar_check = QCheckBox("Show toolbar")
        self.toolbar_check.setChecked(True)
        layout_settings_layout.addRow("", self.toolbar_check)
        
        self.statusbar_check = QCheckBox("Show status bar")
        self.statusbar_check.setChecked(True)
        layout_settings_layout.addRow("", self.statusbar_check)
        
        display_layout.addWidget(layout_settings)
        display_layout.addStretch()
        
        # Notifications tab
        notifications_tab = QWidget()
        notifications_layout = QVBoxLayout(notifications_tab)
        
        # Email notifications
        email_settings = QGroupBox("Email Notifications")
        email_settings_layout = QVBoxLayout(email_settings)
        
        self.email_enabled = QCheckBox("Enable email notifications")
        self.email_enabled.setChecked(True)
        email_settings_layout.addWidget(self.email_enabled)
        
        notification_types = QWidget()
        notification_types_layout = QVBoxLayout(notification_types)
        notification_types_layout.setContentsMargins(20, 0, 0, 0)
        
        self.notify_uploads = QCheckBox("Document uploads")
        self.notify_uploads.setChecked(True)
        notification_types_layout.addWidget(self.notify_uploads)
        
        self.notify_shares = QCheckBox("Document shares")
        self.notify_shares.setChecked(True)
        notification_types_layout.addWidget(self.notify_shares)
        
        self.notify_comments = QCheckBox("Comments")
        self.notify_comments.setChecked(True)
        notification_types_layout.addWidget(self.notify_comments)
        
        self.notify_mentions = QCheckBox("Mentions")
        self.notify_mentions.setChecked(True)
        notification_types_layout.addWidget(self.notify_mentions)
        
        email_settings_layout.addWidget(notification_types)
        
        # Email frequency
        frequency_group = QGroupBox("Email Frequency")
        frequency_layout = QVBoxLayout(frequency_group)
        
        self.immediate_radio = QRadioButton("Send immediately")
        self.immediate_radio.setChecked(True)
        frequency_layout.addWidget(self.immediate_radio)
        
        self.daily_radio = QRadioButton("Daily digest")
        frequency_layout.addWidget(self.daily_radio)
        
        self.weekly_radio = QRadioButton("Weekly digest")
        frequency_layout.addWidget(self.weekly_radio)
        
        email_settings_layout.addWidget(frequency_group)
        
        notifications_layout.addWidget(email_settings)
        
        # Desktop notifications
        desktop_settings = QGroupBox("Desktop Notifications")
        desktop_settings_layout = QVBoxLayout(desktop_settings)
        
        self.desktop_enabled = QCheckBox("Enable desktop notifications")
        self.desktop_enabled.setChecked(True)
        desktop_settings_layout.addWidget(self.desktop_enabled)
        
        desktop_types = QWidget()
        desktop_types_layout = QVBoxLayout(desktop_types)
        desktop_types_layout.setContentsMargins(20, 0, 0, 0)
        
        self.desktop_uploads = QCheckBox("Document uploads")
        self.desktop_uploads.setChecked(True)
        desktop_types_layout.addWidget(self.desktop_uploads)
        
        self.desktop_shares = QCheckBox("Document shares")
        self.desktop_shares.setChecked(True)
        desktop_types_layout.addWidget(self.desktop_shares)
        
        self.desktop_comments = QCheckBox("Comments")
        self.desktop_comments.setChecked(True)
        desktop_types_layout.addWidget(self.desktop_comments)
        
        desktop_settings_layout.addWidget(desktop_types)
        
        notifications_layout.addWidget(desktop_settings)
        notifications_layout.addStretch()
        
        # Security tab
        security_tab = QWidget()
        security_layout = QVBoxLayout(security_tab)
        
        # Login settings
        login_settings = QGroupBox("Login Settings")
        login_settings_layout = QFormLayout(login_settings)
        
        self.remember_check = QCheckBox("Remember login credentials")
        login_settings_layout.addRow("", self.remember_check)
        
        self.auto_login_check = QCheckBox("Auto-login on startup")
        login_settings_layout.addRow("", self.auto_login_check)
        
        self.session_combo = QComboBox()
        self.session_combo.addItems(["15 minutes", "30 minutes", "1 hour", "4 hours", "8 hours", "Never expire"])
        self.session_combo.setCurrentIndex(2)  # Default to 1 hour
        login_settings_layout.addRow("Session timeout:", self.session_combo)
        
        security_layout.addWidget(login_settings)
        
        # Two-factor authentication
        tfa_settings = QGroupBox("Two-Factor Authentication")
        tfa_settings_layout = QVBoxLayout(tfa_settings)
        
        self.tfa_enabled = QCheckBox("Enable two-factor authentication")
        tfa_settings_layout.addWidget(self.tfa_enabled)
        
        tfa_methods = QWidget()
        tfa_methods_layout = QVBoxLayout(tfa_methods)
        tfa_methods_layout.setContentsMargins(20, 0, 0, 0)
        
        self.tfa_app = QRadioButton("Authenticator app")
        self.tfa_app.setChecked(True)
        tfa_methods_layout.addWidget(self.tfa_app)
        
        self.tfa_sms = QRadioButton("SMS verification")
        tfa_methods_layout.addWidget(self.tfa_sms)
        
        self.tfa_email = QRadioButton("Email verification")
        tfa_methods_layout.addWidget(self.tfa_email)
        
        tfa_settings_layout.addWidget(tfa_methods)
        
        setup_tfa_btn = QPushButton("Setup Two-Factor Authentication")
        setup_tfa_btn.clicked.connect(self.setup_tfa)
        tfa_settings_layout.addWidget(setup_tfa_btn)
        
        security_layout.addWidget(tfa_settings)
        security_layout.addStretch()
        
        # Integrations tab
        integrations_tab = QWidget()
        integrations_layout = QVBoxLayout(integrations_tab)
        
        # E-Mail integration
        email_integration = QGroupBox("E-Mail Integration")
        email_integration_layout = QVBoxLayout(email_integration)
        
        self.outlook_enabled = QCheckBox("Enable Outlook integration")
        email_integration_layout.addWidget(self.outlook_enabled)
        
        outlook_settings = QWidget()
        outlook_settings_layout = QFormLayout(outlook_settings)
        outlook_settings_layout.setContentsMargins(20, 10, 10, 10)
        
        self.outlook_email = QLineEdit()
        outlook_settings_layout.addRow("Outlook Email:", self.outlook_email)
        
        self.outlook_sync = QCheckBox("Sync emails automatically")
        self.outlook_sync.setChecked(True)
        outlook_settings_layout.addRow("", self.outlook_sync)
        
        self.outlook_attachments = QCheckBox("Download attachments automatically")
        self.outlook_attachments.setChecked(True)
        outlook_settings_layout.addRow("", self.outlook_attachments)
        
        self.outlook_calendar = QCheckBox("Sync calendar events")
        self.outlook_calendar.setChecked(True)
        outlook_settings_layout.addRow("", self.outlook_calendar)
        
        outlook_test_btn = QPushButton("Test Connection")
        outlook_test_btn.clicked.connect(self.test_outlook_connection)
        outlook_settings_layout.addRow("", outlook_test_btn)
        
        email_integration_layout.addWidget(outlook_settings)
        integrations_layout.addWidget(email_integration)
        
        # Document integration
        doc_integration = QGroupBox("Document Integration")
        doc_integration_layout = QVBoxLayout(doc_integration)
        
        self.word_enabled = QCheckBox("Enable Microsoft Word integration")
        self.word_enabled.setChecked(True)
        doc_integration_layout.addWidget(self.word_enabled)
        
        self.excel_enabled = QCheckBox("Enable Microsoft Excel integration")
        self.excel_enabled.setChecked(True)
        doc_integration_layout.addWidget(self.excel_enabled)
        
        self.pdf_enabled = QCheckBox("Enable PDF integration")
        self.pdf_enabled.setChecked(True)
        doc_integration_layout.addWidget(self.pdf_enabled)
        
        integrations_layout.addWidget(doc_integration)
        integrations_layout.addStretch()
        
        # Voice Assistant tab
        voice_assistant_tab = QWidget()
        voice_assistant_layout = QVBoxLayout(voice_assistant_tab)
        
        # Voice settings
        voice_settings = QGroupBox("Voice Assistant Settings")
        voice_settings_layout = QFormLayout(voice_settings)
        
        self.voice_enabled_checkbox = QCheckBox("Enable voice output")
        voice_settings_layout.addRow("", self.voice_enabled_checkbox)
        
        self.language_voice_combo = QComboBox()
        self.language_voice_combo.addItems(["English", "Arabic", "Spanish"])
        voice_settings_layout.addRow("Voice Language:", self.language_voice_combo)
        
        self.gender_combo = QComboBox()
        self.gender_combo.addItems(["Male", "Female"])
        voice_settings_layout.addRow("Voice Gender:", self.gender_combo)
        
        # Voice rate slider
        rate_container = QWidget()
        rate_layout = QHBoxLayout(rate_container)
        rate_layout.setContentsMargins(0, 0, 0, 0)
        
        self.rate_slider = QSlider(Qt.Orientation.Horizontal)
        self.rate_slider.setRange(50, 300)
        self.rate_slider.setValue(150)
        self.rate_slider.valueChanged.connect(self.update_rate_label)
        rate_layout.addWidget(self.rate_slider)
        
        self.rate_value_label = QLabel("150 WPM")
        rate_layout.addWidget(self.rate_value_label)
        
        voice_settings_layout.addRow("Speech Rate:", rate_container)
        
        # Voice volume slider
        volume_container = QWidget()
        volume_layout = QHBoxLayout(volume_container)
        volume_layout.setContentsMargins(0, 0, 0, 0)
        
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(100)
        self.volume_slider.valueChanged.connect(self.update_volume_label)
        volume_layout.addWidget(self.volume_slider)
        
        self.volume_value_label = QLabel("100%")
        volume_layout.addWidget(self.volume_value_label)
        
        voice_settings_layout.addRow("Volume:", volume_container)
        
        # Test voice button
        test_voice_btn = QPushButton("Test Voice")
        test_voice_btn.clicked.connect(self.test_voice)
        voice_settings_layout.addRow("", test_voice_btn)
        
        voice_assistant_layout.addWidget(voice_settings)
        
        # Reminder settings
        reminder_settings = QGroupBox("Reminder Settings")
        reminder_settings_layout = QVBoxLayout(reminder_settings)
        
        self.reminder_notifications = QCheckBox("Enable reminder notifications")
        self.reminder_notifications.setChecked(True)
        reminder_settings_layout.addWidget(self.reminder_notifications)
        
        self.reminder_voice = QCheckBox("Enable voice for reminders")
        self.reminder_voice.setChecked(True)
        reminder_settings_layout.addWidget(self.reminder_voice)
        
        voice_assistant_layout.addWidget(reminder_settings)
        voice_assistant_layout.addStretch()
        
        # Add tabs
        tabs.addTab(general_tab, "General")
        tabs.addTab(display_tab, "Display")
        tabs.addTab(notifications_tab, "Notifications")
        tabs.addTab(security_tab, "Security")
        tabs.addTab(integrations_tab, "Integrations")
        tabs.addTab(voice_assistant_tab, "Voice Assistant")
        
        main_layout.addWidget(tabs)
    
    def browse_location(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Default Save Location")
        if folder:
            self.default_location.setText(folder)
    
    def change_font(self):
        font, ok = QFontDialog.getFont(QFont("Arial", 12), self)
        if ok:
            self.font_label.setText(f"{font.family()}, {font.pointSize()}pt")
    
    def change_color(self, color_type):
        if color_type == "primary":
            color = QColorDialog.getColor(self.primary_color, self, "Select Primary Color")
            if color.isValid():
                self.primary_color = color
                self.primary_color_btn.setStyleSheet(f"background-color: {color.name()};")
        elif color_type == "secondary":
            color = QColorDialog.getColor(self.secondary_color, self, "Select Secondary Color")
            if color.isValid():
                self.secondary_color = color
                self.secondary_color_btn.setStyleSheet(f"background-color: {color.name()};")
        elif color_type == "accent":
            color = QColorDialog.getColor(self.accent_color, self, "Select Accent Color")
            if color.isValid():
                self.accent_color = color
                self.accent_color_btn.setStyleSheet(f"background-color: {color.name()};")
    
    def reset_colors(self):
        # Reset to default colors
        self.primary_color = QColor("#3498db")
        self.secondary_color = QColor("#2ecc71")
        self.accent_color = QColor("#e74c3c")
        
        # Update buttons
        self.primary_color_btn.setStyleSheet(f"background-color: {self.primary_color.name()};")
        self.secondary_color_btn.setStyleSheet(f"background-color: {self.secondary_color.name()};")
        self.accent_color_btn.setStyleSheet(f"background-color: {self.accent_color.name()};")
    
    def setup_tfa(self):
        if not self.tfa_enabled.isChecked():
            self.tfa_enabled.setChecked(True)
        
        # In a real app, this would open a setup wizard for 2FA
        QMessageBox.information(self, "Two-Factor Authentication", "Two-factor authentication setup wizard would launch here.")
    
    def update_rate_label(self, value):
        self.rate_value_label.setText(f"{value} WPM")
    
    def update_volume_label(self, value):
        self.volume_value_label.setText(f"{value}%")
    
    def test_voice(self):
        # Import the assistant module only when needed to avoid circular imports
        from utils.doxly_assistant import DoxlyAssistant
        
        # Create a temporary assistant instance for testing
        temp_assistant = DoxlyAssistant()
        
        # Apply current settings from UI
        language = self.language_voice_combo.currentText()
        gender = self.gender_combo.currentText().lower()
        rate = self.rate_slider.value()
        volume = self.volume_slider.value() / 100.0
        enabled = self.voice_enabled_checkbox.isChecked()
        
        # Configure the assistant with these settings
        temp_assistant.set_voice_language(language)
        temp_assistant.set_voice_gender(gender)
        temp_assistant.set_voice_rate(rate)
        temp_assistant.set_voice_volume(volume)
        temp_assistant.set_voice_enabled(enabled)
        
        # Test the voice
        if enabled:
            temp_assistant.speak("This is a test of the voice settings. How do I sound?")
        else:
            QMessageBox.information(self, "Voice Test", "Voice output is currently disabled. Enable it to test the voice.")
    
    def set_default_config(self):
        """Set default configuration values"""
        defaults = {
            "general": {
                "language": "English",
                "theme": "Light",
                "startup": False,
                "auto_update": True,
                "default_location": str(os.path.join(os.path.expanduser("~"), "Documents", "Doxly")),
                "default_format": "PDF",
                "compress_files": True
            },
            "display": {
                "font_family": "Arial",
                "font_size": 12,
                "primary_color": "#3498db",
                "secondary_color": "#2ecc71",
                "accent_color": "#e74c3c",
                "show_sidebar": True,
                "show_toolbar": True,
                "show_statusbar": True
            },
            "notifications": {
                "email_enabled": True,
                "notify_uploads": True,
                "notify_shares": True,
                "notify_comments": True,
                "notify_mentions": True,
                "email_frequency": "immediate",
                "desktop_enabled": True,
                "desktop_uploads": True,
                "desktop_shares": True,
                "desktop_comments": True
            },
            "security": {
                "remember_login": False,
                "auto_login": False,
                "session_timeout": "1 hour",
                "tfa_enabled": False,
                "tfa_method": "app"
            },
            "integrations": {
                "outlook_enabled": False,
                "outlook_email": "",
                "outlook_sync": True,
                "outlook_attachments": True,
                "outlook_calendar": True,
                "word_enabled": True,
                "excel_enabled": True,
                "pdf_enabled": True
            }
        }
        
        self.config_manager.set_defaults(defaults)
    
    def apply_settings(self):
        """Apply loaded settings to UI components"""
        # General settings
        general = self.config_manager.get("general", {})
        self.language_combo.setCurrentText(general.get("language", "English"))
        self.theme_combo.setCurrentText(general.get("theme", "Light"))
        self.startup_check.setChecked(general.get("startup", False))
        self.update_check.setChecked(general.get("auto_update", True))
        self.default_location.setText(general.get("default_location", ""))
        self.file_format_combo.setCurrentText(general.get("default_format", "PDF"))
        self.compress_check.setChecked(general.get("compress_files", True))
        
        # Display settings
        display = self.config_manager.get("display", {})
        font_family = display.get("font_family", "Arial")
        font_size = display.get("font_size", 12)
        self.font_label.setText(f"{font_family}, {font_size}pt")
        self.font_size_spin.setValue(font_size)
        
        self.primary_color = QColor(display.get("primary_color", "#3498db"))
        self.primary_color_btn.setStyleSheet(f"background-color: {self.primary_color.name()};")
        
        self.secondary_color = QColor(display.get("secondary_color", "#2ecc71"))
        self.secondary_color_btn.setStyleSheet(f"background-color: {self.secondary_color.name()};")
        
        self.accent_color = QColor(display.get("accent_color", "#e74c3c"))
        self.accent_color_btn.setStyleSheet(f"background-color: {self.accent_color.name()};")
        
        self.sidebar_check.setChecked(display.get("show_sidebar", True))
        self.toolbar_check.setChecked(display.get("show_toolbar", True))
        self.statusbar_check.setChecked(display.get("show_statusbar", True))
        
        # Notifications settings
        notifications = self.config_manager.get("notifications", {})
        self.email_enabled.setChecked(notifications.get("email_enabled", True))
        self.notify_uploads.setChecked(notifications.get("notify_uploads", True))
        self.notify_shares.setChecked(notifications.get("notify_shares", True))
        self.notify_comments.setChecked(notifications.get("notify_comments", True))
        self.notify_mentions.setChecked(notifications.get("notify_mentions", True))
        
        email_frequency = notifications.get("email_frequency", "immediate")
        if email_frequency == "immediate":
            self.immediate_radio.setChecked(True)
        elif email_frequency == "daily":
            self.daily_radio.setChecked(True)
        elif email_frequency == "weekly":
            self.weekly_radio.setChecked(True)
        
        self.desktop_enabled.setChecked(notifications.get("desktop_enabled", True))
        self.desktop_uploads.setChecked(notifications.get("desktop_uploads", True))
        self.desktop_shares.setChecked(notifications.get("desktop_shares", True))
        self.desktop_comments.setChecked(notifications.get("desktop_comments", True))
        
        # Security settings
        security = self.config_manager.get("security", {})
        self.remember_check.setChecked(security.get("remember_login", False))
        self.auto_login_check.setChecked(security.get("auto_login", False))
        self.session_combo.setCurrentText(security.get("session_timeout", "1 hour"))
        # Convert string to boolean if needed
        tfa_method = security.get("tfa_method", False)
        if isinstance(tfa_method, str):
            tfa_method = tfa_method.lower() in ['true', 'yes', '1']
        self.tfa_enabled.setChecked(tfa_method)
        
        tfa_method = security.get("tfa_method", "app")
        if tfa_method == "app":
            self.tfa_app.setChecked(True)
        elif tfa_method == "sms":
            self.tfa_sms.setChecked(True)
        elif tfa_method == "email":
            self.tfa_email.setChecked(True)
        
        # Integrations settings
        integrations = self.config_manager.get("integrations", {})
        self.outlook_enabled.setChecked(integrations.get("outlook_enabled", False))
        self.outlook_email.setText(integrations.get("outlook_email", ""))
        self.outlook_sync.setChecked(integrations.get("outlook_sync", True))
        self.outlook_attachments.setChecked(integrations.get("outlook_attachments", True))
        self.outlook_calendar.setChecked(integrations.get("outlook_calendar", True))
        self.word_enabled.setChecked(integrations.get("word_enabled", True))
        self.excel_enabled.setChecked(integrations.get("excel_enabled", True))
        self.pdf_enabled.setChecked(integrations.get("pdf_enabled", True))
        
        # Voice Assistant settings
        voice = self.config_manager.get("voice_assistant", {})
        self.voice_enabled_checkbox.setChecked(voice.get("voice_enabled", False))
        self.language_voice_combo.setCurrentText(voice.get("voice_language", "English"))
        self.gender_combo.setCurrentText(voice.get("voice_gender", "Male"))
        
        rate = voice.get("voice_rate", 150)
        self.rate_slider.setValue(rate)
        self.rate_value_label.setText(f"{rate} WPM")
        
        volume = int(voice.get("voice_volume", 1.0) * 100)
        self.volume_slider.setValue(volume)
        self.volume_value_label.setText(f"{volume}%")
        
        self.reminder_notifications.setChecked(voice.get("reminder_notifications", True))
        self.reminder_voice.setChecked(voice.get("reminder_voice", True))
    
    def collect_settings(self):
        """Collect current settings from UI components"""
        settings = {
            "general": {
                "language": self.language_combo.currentText(),
                "theme": self.theme_combo.currentText(),
                "startup": self.startup_check.isChecked(),
                "auto_update": self.update_check.isChecked(),
                "default_location": self.default_location.text(),
                "default_format": self.file_format_combo.currentText(),
                "compress_files": self.compress_check.isChecked()
            },
            "display": {
                "font_family": self.font_label.text().split(',')[0].strip(),
                "font_size": self.font_size_spin.value(),
                "primary_color": self.primary_color.name(),
                "secondary_color": self.secondary_color.name(),
                "accent_color": self.accent_color.name(),
                "show_sidebar": self.sidebar_check.isChecked(),
                "show_toolbar": self.toolbar_check.isChecked(),
                "show_statusbar": self.statusbar_check.isChecked()
            },
            "notifications": {
                "email_enabled": self.email_enabled.isChecked(),
                "notify_uploads": self.notify_uploads.isChecked(),
                "notify_shares": self.notify_shares.isChecked(),
                "notify_comments": self.notify_comments.isChecked(),
                "notify_mentions": self.notify_mentions.isChecked(),
                "email_frequency": "immediate" if self.immediate_radio.isChecked() else 
                                  "daily" if self.daily_radio.isChecked() else "weekly",
                "desktop_enabled": self.desktop_enabled.isChecked(),
                "desktop_uploads": self.desktop_uploads.isChecked(),
                "desktop_shares": self.desktop_shares.isChecked(),
                "desktop_comments": self.desktop_comments.isChecked()
            },
            "security": {
                "remember_login": self.remember_check.isChecked(),
                "auto_login": self.auto_login_check.isChecked(),
                "session_timeout": self.session_combo.currentText(),
                "tfa_enabled": self.tfa_enabled.isChecked(),
                "tfa_method": "app" if self.tfa_app.isChecked() else 
                              "sms" if self.tfa_sms.isChecked() else "email"
            },
            "integrations": {
                "outlook_enabled": self.outlook_enabled.isChecked(),
                "outlook_email": self.outlook_email.text(),
                "outlook_sync": self.outlook_sync.isChecked(),
                "outlook_attachments": self.outlook_attachments.isChecked(),
                "outlook_calendar": self.outlook_calendar.isChecked(),
                "word_enabled": self.word_enabled.isChecked(),
                "excel_enabled": self.excel_enabled.isChecked(),
                "pdf_enabled": self.pdf_enabled.isChecked()
            }
        }
        
        return settings
    
    def save_settings(self):
        """Save settings to configuration file"""
        # Collect current settings
        settings = self.collect_settings()
        
        # Update config manager
        self.config_manager.update(settings)
        
        # Save to file
        if self.config_manager.save():
            QMessageBox.information(self, "Settings", "Settings saved successfully!")
        else:
            QMessageBox.warning(self, "Settings", "Failed to save settings. Please try again.")
    
    def test_outlook_connection(self):
        # In a real app, this would test the connection to Outlook
        if not self.outlook_email.text():
            QMessageBox.warning(self, "Outlook Integration", "Please enter your Outlook email address first.")
            return
            
        # Simulate connection test
        QMessageBox.information(self, "Outlook Integration", f"Successfully connected to Outlook with account {self.outlook_email.text()}.")
    
    def reset_settings(self):
        # Ask for confirmation
        reply = QMessageBox.question(self, "Reset Settings", "Are you sure you want to reset all settings to default values?", 
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            # Reset configuration to defaults
            self.config_manager.reset()
            
            # Apply default settings to UI
            self.apply_settings()
            
            # Save the default settings
            self.config_manager.save()
            self.startup_check.setChecked(False)
            self.update_check.setChecked(True)
            self.default_location.setText("C:/Users/Documents/Doxly")
            self.file_format_combo.setCurrentIndex(0)  # PDF
            self.compress_check.setChecked(True)
            self.font_label.setText("Arial, 12pt")
            self.font_size_spin.setValue(12)
            self.reset_colors()
            self.sidebar_check.setChecked(True)
            self.toolbar_check.setChecked(True)
            self.statusbar_check.setChecked(True)
            self.email_enabled.setChecked(True)
            self.notify_uploads.setChecked(True)
            self.notify_shares.setChecked(True)
            self.notify_comments.setChecked(True)
            self.notify_mentions.setChecked(True)
            self.immediate_radio.setChecked(True)
            self.desktop_enabled.setChecked(True)
            self.desktop_uploads.setChecked(True)
            self.desktop_shares.setChecked(True)
            self.desktop_comments.setChecked(True)
            self.remember_check.setChecked(False)
            self.auto_login_check.setChecked(False)
            self.session_combo.setCurrentIndex(2)  # 1 hour
            self.tfa_enabled.setChecked(False)
            self.tfa_app.setChecked(True)
            # Reset integration settings
            self.outlook_enabled.setChecked(False)
            self.outlook_email.setText("")
            self.outlook_sync.setChecked(True)
            self.outlook_attachments.setChecked(True)
            self.outlook_calendar.setChecked(True)
            self.word_enabled.setChecked(True)
            self.excel_enabled.setChecked(True)
            self.pdf_enabled.setChecked(True)
            
            QMessageBox.information(self, "Settings", "All settings have been reset to default values.")