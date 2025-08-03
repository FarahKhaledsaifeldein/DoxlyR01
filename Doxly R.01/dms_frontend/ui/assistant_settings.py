import sys
import os
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, 
                             QSlider, QCheckBox, QPushButton, QGroupBox, QFormLayout,
                             QSpinBox, QDoubleSpinBox, QMessageBox)
from PyQt6.QtCore import Qt, QTimer

class AssistantSettingsDialog(QDialog):
    """Dialog for configuring voice assistant settings"""
    
    def __init__(self, assistant, parent=None):
        super().__init__(parent)
        self.assistant = assistant
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the dialog UI"""
        self.setWindowTitle("Voice Assistant Settings")
        self.setMinimumWidth(400)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # Language settings
        language_group = QGroupBox("Language Settings")
        language_layout = QFormLayout()
        
        self.language_combo = QComboBox()
        # Only include English and Arabic as per requirements
        self.language_combo.addItems(["English", "Arabic"])
        self.language_combo.setCurrentText(self.assistant.language)
        language_layout.addRow("Assistant Language:", self.language_combo)
        
        language_group.setLayout(language_layout)
        main_layout.addWidget(language_group)
        
        # Voice settings
        voice_group = QGroupBox("Voice Settings")
        voice_layout = QFormLayout()
        
        # Voice enabled checkbox
        self.voice_enabled_checkbox = QCheckBox("Enable Voice Output")
        self.voice_enabled_checkbox.setChecked(self.assistant.voice_enabled)
        voice_layout.addRow("", self.voice_enabled_checkbox)
        
        # Voice language
        self.voice_language_combo = QComboBox()
        self.voice_language_combo.addItems(["English", "Arabic"])
        self.voice_language_combo.setCurrentText(self.assistant.voice_language)
        voice_layout.addRow("Voice Language:", self.voice_language_combo)
        
        # Voice gender
        self.voice_gender_combo = QComboBox()
        self.voice_gender_combo.addItems(["female", "male"])
        self.voice_gender_combo.setCurrentText(self.assistant.voice_gender)
        voice_layout.addRow("Voice Gender:", self.voice_gender_combo)
        
        # Voice rate
        self.voice_rate_spinner = QSpinBox()
        self.voice_rate_spinner.setRange(50, 300)
        self.voice_rate_spinner.setValue(self.assistant.voice_rate)
        voice_layout.addRow("Speech Rate:", self.voice_rate_spinner)
        
        # Voice volume
        self.voice_volume_spinner = QDoubleSpinBox()
        self.voice_volume_spinner.setRange(0.0, 1.0)
        self.voice_volume_spinner.setSingleStep(0.1)
        self.voice_volume_spinner.setValue(self.assistant.voice_volume)
        voice_layout.addRow("Volume:", self.voice_volume_spinner)
        
        # Test voice button
        self.test_voice_button = QPushButton("Test Voice")
        self.test_voice_button.clicked.connect(self.test_voice)
        voice_layout.addRow("", self.test_voice_button)
        
        voice_group.setLayout(voice_layout)
        main_layout.addWidget(voice_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_settings)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        main_layout.addLayout(button_layout)
    
    def test_voice(self):
        """Test the current voice settings"""
        # Create a temporary copy of settings to test without saving
        temp_voice_enabled = self.assistant.voice_enabled
        temp_voice_language = self.assistant.voice_language
        temp_voice_gender = self.assistant.voice_gender
        temp_voice_rate = self.assistant.voice_rate
        temp_voice_volume = self.assistant.voice_volume
        
        try:
            # Apply current dialog settings temporarily
            self.assistant.set_voice_enabled(self.voice_enabled_checkbox.isChecked())
            self.assistant.set_voice_language(self.voice_language_combo.currentText())
            self.assistant.set_voice_gender(self.voice_gender_combo.currentText())
            self.assistant.set_voice_rate(self.voice_rate_spinner.value())
            self.assistant.set_voice_volume(self.voice_volume_spinner.value())
            
            # Test the voice
            self.assistant.speak("This is a test of the voice settings. How do I sound?")
        except Exception as e:
            QMessageBox.warning(self, "Voice Test Error", f"Error testing voice: {str(e)}")
        finally:
            # Restore original settings
            self.assistant.set_voice_enabled(temp_voice_enabled)
            self.assistant.set_voice_language(temp_voice_language)
            self.assistant.set_voice_gender(temp_voice_gender)
            self.assistant.set_voice_rate(temp_voice_rate)
            self.assistant.set_voice_volume(temp_voice_volume)
    
    def save_settings(self):
        """Save the settings to the assistant"""
        try:
            # Apply all settings
            self.assistant.set_language(self.language_combo.currentText())
            self.assistant.set_voice_enabled(self.voice_enabled_checkbox.isChecked())
            self.assistant.set_voice_language(self.voice_language_combo.currentText())
            self.assistant.set_voice_gender(self.voice_gender_combo.currentText())
            self.assistant.set_voice_rate(self.voice_rate_spinner.value())
            self.assistant.set_voice_volume(self.voice_volume_spinner.value())
            
            QMessageBox.information(self, "Settings Saved", "Voice assistant settings have been updated.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save settings: {str(e)}")