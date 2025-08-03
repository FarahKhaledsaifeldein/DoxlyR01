import sys
import os
import datetime
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, 
                             QTextEdit, QLabel, QScrollArea, QFrame, QSizePolicy, QMenu,
                             QDialog, QListWidget, QListWidgetItem, QMessageBox)
from PyQt6.QtGui import QIcon, QFont, QColor, QAction
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QSize

# Import the settings dialog
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ui.assistant_settings import AssistantSettingsDialog

class AssistantWidget(QWidget):
    """Widget for interacting with the Doxly Assistant"""
    
    def __init__(self, parent=None, token=None, username=None):
        super().__init__(parent)
        self.token = token
        self.username = username
        self.assistant = None
        self.voice_command_handler = None
        self.is_listening = False
        
        # Initialize the assistant
        self.init_assistant()
        
        # Set up the UI
        self.setup_ui()
        
        # Start the reminder checker
        self.reminder_timer = QTimer(self)
        self.reminder_timer.timeout.connect(self.check_reminders)
        self.reminder_timer.start(60000)  # Check every minute
    
    def init_assistant(self):
        """Initialize the assistant"""
        from .doxly_assistant import DoxlyAssistant
        from .voice_commands import VoiceCommandHandler
        
        self.assistant = DoxlyAssistant()
        if self.username:
            self.assistant.username = self.username
        if self.token:
            self.assistant.token = self.token
        
        # Initialize voice command handler
        self.voice_command_handler = VoiceCommandHandler()
        self.voice_command_handler.command_detected.connect(self.process_voice_command)
        self.voice_command_handler.error_occurred.connect(self.handle_voice_error)
    
    def setup_ui(self):
        """Set up the widget UI"""
        self.setWindowTitle("Doxly Assistant")
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Chat display area
        self.chat_area = QScrollArea()
        self.chat_area.setWidgetResizable(True)
        self.chat_area.setFrameShape(QFrame.Shape.NoFrame)
        
        self.chat_widget = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_widget)
        self.chat_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.chat_layout.setSpacing(10)
        
        self.chat_area.setWidget(self.chat_widget)
        main_layout.addWidget(self.chat_area, 1)
        
        # Add a welcome message
        self.add_assistant_message("Hello! I'm Doxly, your assistant. How can I help you today?")
        
        # Input area
        input_layout = QHBoxLayout()
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type your message here...")
        self.input_field.returnPressed.connect(self.send_message)
        
        self.send_button = QPushButton()
        self.send_button.setIcon(QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "icons", "send.png")))
        self.send_button.setFixedSize(36, 36)
        self.send_button.clicked.connect(self.send_message)
        
        self.voice_button = QPushButton()
        self.voice_button.setIcon(QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "icons", "mic.png")))
        self.voice_button.setFixedSize(36, 36)
        self.voice_button.clicked.connect(self.toggle_voice_input)
        
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.voice_button)
        input_layout.addWidget(self.send_button)
        
        main_layout.addLayout(input_layout)
        
        # Bottom toolbar
        toolbar_layout = QHBoxLayout()
        
        self.settings_button = QPushButton("Settings")
        self.settings_button.clicked.connect(self.show_settings)
        
        self.reminders_button = QPushButton("Reminders")
        self.reminders_button.clicked.connect(self.show_reminders)
        
        toolbar_layout.addWidget(self.settings_button)
        toolbar_layout.addWidget(self.reminders_button)
        toolbar_layout.addStretch()
        
        main_layout.addLayout(toolbar_layout)
    
    def add_user_message(self, message):
        """Add a user message to the chat"""
        message_widget = QFrame()
        message_widget.setFrameShape(QFrame.Shape.StyledPanel)
        message_widget.setStyleSheet(
            "background-color: #e1f5fe; border-radius: 10px; padding: 8px;"
        )
        
        message_layout = QVBoxLayout(message_widget)
        message_layout.setContentsMargins(10, 5, 10, 5)
        
        # Add user label
        user_label = QLabel("You")
        user_label.setStyleSheet("font-weight: bold; color: #0277bd;")
        message_layout.addWidget(user_label)
        
        # Add message text
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        message_layout.addWidget(message_label)
        
        # Add to chat layout, right-aligned
        container = QHBoxLayout()
        container.addStretch()
        container.addWidget(message_widget)
        self.chat_layout.addLayout(container)
        
        # Scroll to bottom
        self.chat_area.verticalScrollBar().setValue(
            self.chat_area.verticalScrollBar().maximum()
        )
    
    def add_assistant_message(self, message):
        """Add an assistant message to the chat"""
        message_widget = QFrame()
        message_widget.setFrameShape(QFrame.Shape.StyledPanel)
        message_widget.setStyleSheet(
            "background-color: #f5f5f5; border-radius: 10px; padding: 8px;"
        )
        
        message_layout = QVBoxLayout(message_widget)
        message_layout.setContentsMargins(10, 5, 10, 5)
        
        # Add assistant label
        assistant_label = QLabel("Doxly")
        assistant_label.setStyleSheet("font-weight: bold; color: #424242;")
        message_layout.addWidget(assistant_label)
        
        # Add message text
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        message_layout.addWidget(message_label)
        
        # Add to chat layout, left-aligned
        container = QHBoxLayout()
        container.addWidget(message_widget)
        container.addStretch()
        self.chat_layout.addLayout(container)
        
        # Scroll to bottom
        self.chat_area.verticalScrollBar().setValue(
            self.chat_area.verticalScrollBar().maximum()
        )
    
    def send_message(self):
        """Send a message to the assistant"""
        message = self.input_field.text().strip()
        if not message:
            return
        
        # Add user message to chat
        self.add_user_message(message)
        
        # Clear input field
        self.input_field.clear()
        
        # Disable input while processing
        self.input_field.setEnabled(False)
        self.send_button.setEnabled(False)
        
        # Add a "thinking" message
        self.add_assistant_message("Thinking...")
        
        try:
            # Process message and get response
            response = self.assistant.process_query(message)
            
            # Remove the "thinking" message
            self._remove_last_message()
            
            # Add assistant response to chat
            self.add_assistant_message(response)
        except Exception as e:
            # Remove the "thinking" message
            self._remove_last_message()
            
            # Add error message
            self.add_assistant_message(f"Sorry, I encountered an error: {str(e)}")
        finally:
            # Re-enable input
            self.input_field.setEnabled(True)
            self.send_button.setEnabled(True)
            self.input_field.setFocus()
    
    def _remove_last_message(self):
        """Remove the last message from the chat layout"""
        if self.chat_layout.count() > 0:
            # Get the last item in the layout
            last_item = self.chat_layout.itemAt(self.chat_layout.count() - 1)
            if last_item:
                # Remove the layout and all its widgets
                while last_item.count():
                    widget = last_item.itemAt(0).widget()
                    if widget:
                        widget.setParent(None)
                    last_item.removeItem(last_item.itemAt(0))
                self.chat_layout.removeItem(last_item)
    
    def toggle_voice_input(self):
        """Toggle voice input mode"""
        if self.is_listening:
            # Stop listening
            self.is_listening = False
            self.voice_command_handler.is_listening = False
            self.voice_button.setIcon(QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "icons", "mic.png")))
            self.add_assistant_message("Voice input disabled.")
            
            # Stop the voice command handler thread if it's running
            if self.voice_command_handler.isRunning():
                self.voice_command_handler.quit()
                self.voice_command_handler.wait(1000)  # Wait up to 1 second for thread to finish
        else:
            # Start listening
            self.is_listening = True
            self.voice_command_handler.is_listening = True
            self.voice_button.setIcon(QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "icons", "mic-active.png")))
            self.add_assistant_message("Listening for voice commands...")
            
            # Start the voice command handler in a separate thread
            if not self.voice_command_handler.isRunning():
                self.voice_command_handler.start()
    
    def process_voice_command(self, command):
        """Process a voice command"""
        self.add_user_message(command)
        
        # Add a "thinking" message
        self.add_assistant_message("Thinking...")
        
        try:
            # Process command and get response
            response = self.assistant.process_query(command)
            
            # Remove the "thinking" message
            self._remove_last_message()
            
            # Add assistant response to chat
            self.add_assistant_message(response)
        except Exception as e:
            # Remove the "thinking" message
            self._remove_last_message()
            
            # Add error message
            self.add_assistant_message(f"Sorry, I encountered an error: {str(e)}")
        finally:
            # Make sure input is enabled
            self.input_field.setEnabled(True)
            self.send_button.setEnabled(True)
    
    def handle_voice_error(self, error_message):
        """Handle voice recognition errors"""
        self.add_assistant_message(f"Error: {error_message}")
        self.is_listening = False
        self.voice_button.setIcon(QIcon(os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "icons", "mic.png")))
    
    def show_settings(self):
        """Show the assistant settings dialog"""
        dialog = AssistantSettingsDialog(self.assistant, self)
        if dialog.exec():
            # Settings were saved, update UI if needed
            # Update voice button state if voice was disabled
            if not self.assistant.voice_enabled and self.is_listening:
                self.toggle_voice_input()  # Turn off voice input if voice was disabled
            
            # Update any UI elements that depend on assistant settings
            self.add_assistant_message(f"Settings updated. Language set to {self.assistant.language}.")
            
            # If voice is enabled, speak the confirmation
            if self.assistant.voice_enabled:
                self.assistant.speak("Settings have been updated.")
    
    def show_reminders(self):
        """Show the reminders dialog"""
        dialog = ReminderDialog(self.assistant, self)
        dialog.exec()
    
    def check_reminders(self):
        """Check for due reminders"""
        due_reminders = self.assistant.check_due_reminders()
        for reminder in due_reminders:
            self.show_reminder_notification(reminder)
    
    def show_reminder_notification(self, reminder):
        """Show a notification for a due reminder"""
        message = f"Reminder: {reminder['task']}"
        self.add_assistant_message(message)
        
        # Also speak the reminder if voice is enabled
        if self.assistant.voice_enabled:
            self.assistant.speak(message)

class ReminderDialog(QDialog):
    """Dialog for managing reminders"""
    
    def __init__(self, assistant, parent=None):
        super().__init__(parent)
        self.assistant = assistant
        self.setup_ui()
        self.load_reminders()
    
    def setup_ui(self):
        """Set up the dialog UI"""
        self.setWindowTitle("Reminders")
        self.setMinimumWidth(400)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # Reminders list
        self.reminders_list = QListWidget()
        main_layout.addWidget(self.reminders_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.add_button = QPushButton("Add Reminder")
        self.add_button.clicked.connect(self.add_reminder)
        
        self.remove_button = QPushButton("Remove Selected")
        self.remove_button.clicked.connect(self.remove_reminder)
        
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.remove_button)
        button_layout.addWidget(self.close_button)
        
        main_layout.addLayout(button_layout)
    
    def load_reminders(self):
        """Load reminders from the assistant"""
        self.reminders_list.clear()
        
        reminders = self.assistant.get_active_reminders()
        for reminder in reminders:
            time_str = reminder['time'].strftime("%Y-%m-%d %H:%M")
            item = QListWidgetItem(f"{time_str} - {reminder['task']}")
            item.setData(Qt.ItemDataRole.UserRole, reminder)
            self.reminders_list.addItem(item)
    
    def add_reminder(self):
        """Add a new reminder"""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QDateTimeEdit, QPushButton
        from PyQt6.QtCore import QDateTime
        
        # Create a dialog for adding a reminder
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Reminder")
        dialog.setMinimumWidth(350)
        
        # Set up the dialog layout
        layout = QVBoxLayout(dialog)
        
        # Task input
        task_layout = QHBoxLayout()
        task_label = QLabel("Task:")
        task_input = QLineEdit()
        task_layout.addWidget(task_label)
        task_layout.addWidget(task_input)
        layout.addLayout(task_layout)
        
        # Time input
        time_layout = QHBoxLayout()
        time_label = QLabel("Time:")
        time_input = QDateTimeEdit(QDateTime.currentDateTime().addSecs(3600))  # Default to 1 hour from now
        time_input.setDisplayFormat("yyyy-MM-dd HH:mm")
        time_input.setCalendarPopup(True)
        time_layout.addWidget(time_label)
        time_layout.addWidget(time_input)
        layout.addLayout(time_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        cancel_button = QPushButton("Cancel")
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
        # Connect buttons
        save_button.clicked.connect(dialog.accept)
        cancel_button.clicked.connect(dialog.reject)
        
        # Show the dialog
        if dialog.exec():
            task = task_input.text().strip()
            reminder_time = time_input.dateTime().toPyDateTime()
            
            if task:
                # Add the reminder
                self.assistant.reminders.append({
                    "task": task,
                    "time": reminder_time,
                    "completed": False
                })
                
                # Show confirmation
                time_str = reminder_time.strftime("%Y-%m-%d %H:%M")
                QMessageBox.information(self, "Reminder Added", 
                                      f"Reminder set for {time_str}: {task}")
                
                # Reload the reminders list
                self.load_reminders()
            else:
                QMessageBox.warning(self, "Invalid Input", "Please enter a task description.")
    
    def remove_reminder(self):
        """Remove the selected reminder"""
        selected_items = self.reminders_list.selectedItems()
        if not selected_items:
            return
        
        # Get the reminder data from the selected item
        reminder = selected_items[0].data(Qt.ItemDataRole.UserRole)
        
        # Remove the reminder from the assistant's list
        if reminder in self.assistant.reminders:
            self.assistant.reminders.remove(reminder)
            QMessageBox.information(self, "Reminder Removed", 
                                  f"Reminder '{reminder['task']}' has been removed.")
        else:
            QMessageBox.warning(self, "Reminder Not Found", 
                              "Could not find the selected reminder.")
        
        # Reload the reminders list
        self.load_reminders()