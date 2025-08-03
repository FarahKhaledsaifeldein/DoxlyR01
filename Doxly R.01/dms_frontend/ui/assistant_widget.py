from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
                             QFrame, QSizePolicy, QDialog, QMessageBox, QToolButton,
                             QMenu)
from PyQt6.QtGui import QIcon, QFont, QColor, QAction
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QTimer
import os
import sys

# Add the parent directory to sys.path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  
from utils.doxly_assistant import AssistantWidget, DoxlyAssistant, ReminderDialog

class FloatingAssistantButton(QToolButton):
    """Floating button that opens the assistant when clicked"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(60, 60)
        self.setIconSize(QSize(40, 40))
        
        # Set icon - use a placeholder if the actual icon doesn't exist
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "icons", "assistant.png")
        if os.path.exists(icon_path):
            self.setIcon(QIcon(icon_path))
        else:
            # Set a text label as fallback
            self.setText("Doxly")
            self.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        
        # Style the button
        self.setStyleSheet("""
            QToolButton {
                background-color: #3498db;
                color: white;
                border-radius: 30px;
                border: 2px solid #2980b9;
            }
            QToolButton:hover {
                background-color: #2980b9;
            }
            QToolButton:pressed {
                background-color: #1f6dad;
            }
        """)
        
        # Add tooltip
        self.setToolTip("Click to open Doxly Assistant")
        
        # Set up context menu
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
    
    def show_context_menu(self, pos):
        """Show context menu with quick actions"""
        menu = QMenu(self)
        
        # Add quick actions
        actions = [
            ("Ask a question", self.parent().open_assistant if self.parent() else None),
            ("Set a reminder", self.parent().open_reminders if self.parent() else None),
            ("Voice command", self.parent().start_voice_command if self.parent() else None)
        ]
        
        for text, slot in actions:
            action = QAction(text, self)
            if slot:
                action.triggered.connect(slot)
            menu.addAction(action)
        
        # Show the menu
        menu.exec(self.mapToGlobal(pos))


class AssistantIntegration(QWidget):
    """Widget that integrates the assistant into the main application"""
    
    def __init__(self, parent=None, token=None, username=None):
        super().__init__(parent)
        self.token = token
        self.username = username
        self.assistant = DoxlyAssistant()
        self.assistant_widget = None
        self.floating_button = None
        
        # Set up the UI
        self.setup_ui()
        
        # Register cleanup handler with main window if available
        if parent and hasattr(parent, 'register_cleanup'):
            parent.register_cleanup(self.cleanup)
    
    def setup_ui(self):
        # Create floating button
        self.floating_button = FloatingAssistantButton(self.parent())
        self.floating_button.clicked.connect(self.toggle_assistant)
        
        # Position the button in the bottom-right corner of the parent widget
        self.position_floating_button()
        
        # Show the button
        self.floating_button.show()
        
        # Create assistant widget (hidden initially)
        self.assistant_widget = AssistantWidget(self.parent(), self.token, self.username)
        self.assistant_widget.setFixedSize(350, 500)
        self.assistant_widget.hide()
    
    def position_floating_button(self):
        """Position the floating button in the bottom-right corner"""
        if self.parent():
            parent_rect = self.parent().rect()
            button_x = parent_rect.width() - self.floating_button.width() - 20
            button_y = parent_rect.height() - self.floating_button.height() - 20
            self.floating_button.move(button_x, button_y)
    
    def toggle_assistant(self):
        """Toggle the assistant widget visibility"""
        if self.assistant_widget.isVisible():
            self.assistant_widget.hide()
        else:
            # Position the assistant widget near the button
            self.position_assistant_widget()
            self.assistant_widget.show()
    
    def position_assistant_widget(self):
        """Position the assistant widget above the floating button"""
        if self.parent() and self.floating_button:
            button_pos = self.floating_button.pos()
            widget_x = button_pos.x() - self.assistant_widget.width() + self.floating_button.width()
            widget_y = button_pos.y() - self.assistant_widget.height() - 10
            
            # Ensure the widget stays within the parent's bounds
            if widget_x < 0:
                widget_x = 0
            if widget_y < 0:
                widget_y = 0
            
            self.assistant_widget.move(widget_x, widget_y)
    
    def open_assistant(self):
        """Open the assistant widget"""
        if not self.assistant_widget.isVisible():
            self.position_assistant_widget()
            self.assistant_widget.show()
    
    def open_reminders(self):
        """Open the reminders dialog"""
        dialog = ReminderDialog(self.assistant, self.parent())
        dialog.exec()
    
    def start_voice_command(self):
        """Start voice command mode"""
        self.open_assistant()
        self.assistant_widget.toggle_voice_input()
    
    def cleanup(self):
        """Clean up resources used by the assistant"""
        if self.assistant_widget:
            self.assistant_widget.hide()
        if self.floating_button:
            self.floating_button.hide()
    
    def resizeEvent(self, event):
        """Handle resize events to reposition the floating button"""
        self.position_floating_button()
        super().resizeEvent(event)


def integrate_assistant(main_window, token=None, username=None):
    """Integrate the assistant into the main window"""
    # Create and return the assistant integration
    return AssistantIntegration(main_window, token, username)