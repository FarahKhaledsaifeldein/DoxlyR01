from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QStackedWidget, QPushButton, QLabel, QFrame, 
                             QMenu, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon
from utils.voice_commands import VoiceCommandHandler
from ui.assistant_widget import integrate_assistant
from functools import partial
import os

class MainWindow(QMainWindow):
    def __init__(self, token, username):
        super().__init__()
        
        self.token = token
        self.username = username
        print(f"[DEBUG] MainWindow initialized with username: {self.username}")
        self.setWindowTitle(f"Doxly Document Management System - {self.username}")
        self.setMinimumSize(1200, 800)
        
        # Track current page and state
        self.current_page = "home"
        self.page_states = {}
        self.cleanup_handlers = []

        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        
        # Create sidebar with username and main_window reference
        self.sidebar = SidebarWidget(username=self.username, main_window=self)
        print(f"[DEBUG] Sidebar created with username: {self.username}")

        # Initialize voice command handler
        self.voice_handler = VoiceCommandHandler()
        self.voice_handler.command_detected.connect(self.handle_voice_command)
        self.voice_handler.error_occurred.connect(self.handle_voice_error)
        self.voice_handler.start()
        
        # Create stacked widget for different pages
        self.stack = QStackedWidget()
        
        # Import and initialize pages
        from .dashboard_page import DashboardPage
        from .document_page import DocumentPage
        from .project_page import ProjectPage
        
        # Create specialized pages
        from .templates_page import TemplatesPage
        from .analysis_page import AnalysisPage
        from .email_page import EmailPage
        from .settings_page import SettingsPage
        from .user_preferences_page import UserPreferencesPage
        
        # Add pages to stack
        self.pages = {
            "home": DashboardPage(token=self.token, username=self.username),
            "documents": DocumentPage(token=self.token, username=self.username),
            "projects": ProjectPage(token=self.token, username=self.username),
            "analytics": AnalysisPage(token=self.token, username=self.username),
            "templates": TemplatesPage(token=self.token, username=self.username),
            "email": EmailPage(token=self.token, username=self.username),
            "support": QWidget(),
            "settings": SettingsPage(token=self.token, username=self.username),
            "preferences": UserPreferencesPage(token=self.token, username=self.username)
        }
        
        for page_name, page in self.pages.items():
            self.stack.addWidget(page)
            if hasattr(page, 'set_username'):
                page.set_username(self.username)
        
        # Add widgets to main layout
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.stack)
        
        # Set default page to Home
        self.switch_page("home")
        
        # Initialize Doxly Assistant
        self.assistant = integrate_assistant(self, token=self.token, username=self.username)
        print(f"[DEBUG] Assistant initialized with username: {self.username}")
        
    def switch_page(self, page_name):
        if page_name in self.pages:
            # Save current page state if needed
            if hasattr(self.pages[self.current_page], 'save_state'):
                self.page_states[self.current_page] = self.pages[self.current_page].save_state()
            
            # Switch to new page
            self.stack.setCurrentWidget(self.pages[page_name])
            self.current_page = page_name
            
            # Restore page state if exists
            if page_name in self.page_states and hasattr(self.pages[page_name], 'restore_state'):
                self.pages[page_name].restore_state(self.page_states[page_name])
            
            # Update sidebar
            self.sidebar.update_active_page(page_name)
    
    def handle_voice_command(self, command):
        command_actions = {
            "upload": lambda: self.switch_page("documents"),
            "share": lambda: self.switch_page("documents"),
            "list": lambda: self.switch_page("documents"),
            "templates": lambda: self.switch_page("templates"),
            "analysis": lambda: self.switch_page("analytics"),
            "email": lambda: self.switch_page("email"),
            "settings": lambda: self.switch_page("settings"),
            "assistant": lambda: self.toggle_assistant() if hasattr(self, 'assistant') else None,
            "reminder": lambda: self.open_assistant_reminders() if hasattr(self, 'assistant') else None,
            "logout": self.logout
        }
        
        if command in command_actions:
            command_actions[command]()
            if hasattr(self, 'assistant') and hasattr(self.assistant, 'assistant_widget'):
                if self.assistant.assistant_widget.isVisible():
                    self.assistant.assistant_widget.add_assistant_message(f"Executing command: {command}")
        elif hasattr(self, 'assistant') and hasattr(self.assistant, 'assistant_widget'):
            self.assistant.open_assistant()
            self.assistant.assistant_widget.process_voice_command(command)
    
    def handle_voice_error(self, error):
        print(f"Voice recognition error: {error}")
        
    def toggle_assistant(self):
        if hasattr(self, 'assistant'):
            self.assistant.toggle_assistant()
            
    def open_assistant_reminders(self):
        if hasattr(self, 'assistant'):
            self.assistant.open_reminders()
        
    def logout(self):
        if hasattr(self, 'voice_handler'):
            self.voice_handler.stop()
        
        for cleanup_handler in self.cleanup_handlers:
            try:
                cleanup_handler()
            except Exception as e:
                print(f"Error during cleanup: {e}")
        
        self.token = None
        self.username = None
        
        from .login_window import LoginWindow
        self.login_window = LoginWindow()
        self.login_window.show()
        self.close()
    
    def register_cleanup(self, handler):
        self.cleanup_handlers.append(handler)
    
    def closeEvent(self, event):
        if hasattr(self, 'voice_handler'):
            self.voice_handler.stop()
        
        for cleanup_handler in self.cleanup_handlers:
            try:
                cleanup_handler()
            except Exception as e:
                print(f"Error during cleanup: {e}")
        
        super().closeEvent(event)
    
    def resizeEvent(self, event):
        if hasattr(self, 'assistant'):
            self.assistant.position_floating_button()
        super().resizeEvent(event)

    def update_username(self, new_username):
        """Update the username throughout the application"""
        print(f"[DEBUG] Updating username to: {new_username}")
        self.username = new_username
        self.setWindowTitle(f"Doxly Document Management System - {self.username}")
        self.sidebar.update_username(self.username)
        
        # Update username in all pages that need it
        for page_name, page in self.pages.items():
            if hasattr(page, 'set_username'):
                page.set_username(new_username)
            if hasattr(page, 'update_username'):
                page.update_username(new_username)
        
        # Update assistant if it exists
        if hasattr(self, 'assistant') and hasattr(self.assistant, 'set_username'):
            self.assistant.set_username(new_username)

class SidebarWidget(QWidget):
    def __init__(self, username=None, main_window=None):
        super().__init__()
        print(f"[DEBUG] SidebarWidget initialized with username: {username}")
        self.setObjectName("Sidebar")
        self.setFixedWidth(250)
        self.main_window = main_window
        self.nav_buttons = {}
        self.current_active = None
        self.username= username or "User"
        sidebar_layout = QVBoxLayout(self)
        sidebar_layout.setContentsMargins(10, 20, 10, 20)
        sidebar_layout.setSpacing(15)
        
        # Profile Section
        profile_frame = QFrame()
        profile_layout = QHBoxLayout(profile_frame)
        profile_layout.setContentsMargins(10, 0, 10, 0)
        
        # Profile image with initials
        self.profile_img = QLabel()
        self.profile_img.setFixedSize(40, 40)
        self.profile_img.setStyleSheet("""
            background-color: #3498db; 
            border-radius: 20px;
            color: white;
            font-weight: bold;
            font-size: 16px;
        """)
        self.profile_img.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.update_profile_initials(self.username)
        
        profile_layout.addWidget(self.profile_img)
        
        # Profile button
        self.profile_btn = QPushButton(self.username)
        self.profile_btn.setStyleSheet("""
            QPushButton {
                background: none;
                border: none;
                text-align: left;
                font-size: 14px;
                font-weight: bold;
                padding: 0;
                margin: 0;
                min-width: 120px;
            }
            QPushButton:hover {
                color: #3498db;
            }
        """)
        print(f"[DEBUG] Profile button text set to: {username if username else 'User'}")
        
        # Profile menu
        profile_menu = QMenu(self)
        profile_menu.setStyleSheet("""
            QMenu {
                background-color: white;
                border: 1px solid #dcdcdc;
                border-radius: 4px;
                padding: 5px;
            }
            QMenu::item {
                padding: 8px 20px;
                color: #2c3e50;
            }
            QMenu::item:selected {
                background-color: #f0f0f0;
                color: #3498db;
            }
        """)
        
        # Add menu actions
        profile_pref_action = profile_menu.addAction("Profile Preferences")
        logout_action = profile_menu.addAction("Logout")
        
        # Connect actions if main_window is provided
        if main_window:
            profile_pref_action.triggered.connect(lambda: main_window.switch_page("preferences"))
            logout_action.triggered.connect(main_window.logout)
        
        self.profile_btn.setMenu(profile_menu)
        profile_layout.addWidget(self.profile_btn)
        sidebar_layout.addWidget(profile_frame)
        
        # Navigation Items
        sidebar_items = [
            ("Home", "🏠", "home"),
            ("Documents", "📄", "documents"),
            ("Project Files", "📂", "projects"), 
            ("Templates", "📝", "templates"),
            ("Analysis", "📊", "analytics"),
            ("E-Mail", "📧", "email"),
            ("Support", "❓", "support"),
            ("Settings", "⚙️", "settings")
        ]
        
        for text, icon, page in sidebar_items:
            btn = QPushButton(f"{icon}  {text}")
            btn.setStyleSheet("""
                QPushButton {
                    text-align: left;
                    padding: 8px;
                    border: none;
                    border-radius: 4px;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background-color: rgba(52, 152, 219, 0.1);
                    color: #3498db;
                }
                QPushButton[active="true"] {
                    background-color: rgba(52, 152, 219, 0.2);
                    color: #3498db;
                    font-weight: bold;
                }
            """)
            
            if page and main_window:
                btn.clicked.connect(partial(main_window.switch_page, page))
                self.nav_buttons[page] = btn
                
            sidebar_layout.addWidget(btn)
        
        # Spacer and version info
        sidebar_layout.addStretch()
        
        version_frame = QFrame()
        version_layout = QVBoxLayout(version_frame)
        version_label = QLabel("Doxly v1.0")
        version_label.setStyleSheet("color: #7f8c8d; font-size: 11px;")
        version_layout.addWidget(version_label)
        sidebar_layout.addWidget(version_frame)
    
    def update_profile_initials(self, username):
        username = username or "user"
        initials = username[0].upper()
        """Update the profile image initials"""
        #initials = "U"  # Default
        if username:
            name_parts = username.split()
            if len(name_parts) > 1:
                initials = f"{name_parts[0][0].upper()}{name_parts[-1][0].upper()}"
            else:
                initials = username[0].upper()
        print(f"[DEBUG] Setting profile initials to: {initials}")
        self.profile_img.setText(initials)
    
    def update_username(self, new_username):
        """Update the displayed username"""
        print(f"[DEBUG] Updating sidebar username to: {new_username}")
        self.username = new_username
        self.profile_btn.setText(new_username if new_username else "User")
        self.update_profile_initials(new_username)
    
    def update_active_page(self, page_name):
        """Update the active navigation button"""
        if self.current_active in self.nav_buttons:
            self.nav_buttons[self.current_active].setProperty("active", False)
            self.nav_buttons[self.current_active].style().unpolish(self.nav_buttons[self.current_active])
            self.nav_buttons[self.current_active].style().polish(self.nav_buttons[self.current_active])
        
        if page_name in self.nav_buttons:
            self.nav_buttons[page_name].setProperty("active", True)
            self.nav_buttons[page_name].style().unpolish(self.nav_buttons[page_name])
            self.nav_buttons[page_name].style().polish(self.nav_buttons[page_name])
            self.current_active = page_name