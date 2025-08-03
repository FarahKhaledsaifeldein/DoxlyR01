from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QLineEdit,
                             QPushButton, QLabel, QFrame, QMessageBox, QStackedWidget)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from api.auth_api import AuthAPI
from ui.main_window import MainWindow
from datetime import datetime
from datetime import datetime

# Inside LoginWindow class


class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Doxly - Login")
        self.setFixedSize(400, 600)
        self.auth_api = AuthAPI()
        
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        
        # Create stacked widget for login and registration
        self.stack = QStackedWidget()
        main_layout.addWidget(self.stack)
        
        # Create login page
        login_page = QWidget()
        login_layout = QVBoxLayout(login_page)
        login_layout.setSpacing(20)
        login_layout.setContentsMargins(40, 40, 40, 40)
        
        # Add logo and title
        title = QLabel("Doxly")
        title.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                font-size: 32px;
                font-weight: bold;
            }
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        login_layout.addWidget(title)
        
        subtitle = QLabel("Document Management System")
        subtitle.setStyleSheet("color: #7f8c8d; font-size: 16px;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        login_layout.addWidget(subtitle)
        
        login_layout.addSpacing(40)
        
        # Login form
        self.username = QLineEdit()
        self.username.setPlaceholderText("Username")
        self.username.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)
        login_layout.addWidget(self.username)
        
        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.password.setStyleSheet(self.username.styleSheet())
        login_layout.addWidget(self.password)
        
        # Login button
        login_button = QPushButton("Login")
        login_button.setStyleSheet("""
            QPushButton {
                background-color: #2c3e50;
                color: white;
                border: none;
                padding: 12px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #34495e;
            }
            QPushButton:pressed {
                background-color: #2c3e50;
            }
        """)
        login_button.clicked.connect(self.handle_login)
        login_layout.addWidget(login_button)
        
        # Register link
        register_link = QPushButton("Don't have an account? Register")
        register_link.setStyleSheet("""
            QPushButton {
                background: none;
                border: none;
                color: #3498db;
                text-decoration: underline;
            }
            QPushButton:hover {
                color: #2980b9;
            }
        """)
        register_link.clicked.connect(lambda: self.stack.setCurrentWidget(register_page))
        login_layout.addWidget(register_link)
        
        login_layout.addStretch()
        
        # Create registration page
        register_page = QWidget()
        register_layout = QVBoxLayout(register_page)
        register_layout.setSpacing(20)
        register_layout.setContentsMargins(40, 40, 40, 40)
        
        # Registration title
        register_title = QLabel("Create Account")
        register_title.setStyleSheet(title.styleSheet())
        register_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        register_layout.addWidget(register_title)
        
        register_layout.addSpacing(40)
        
        # Registration form
        self.reg_username = QLineEdit()
        self.reg_username.setPlaceholderText("Username")
        self.reg_username.setStyleSheet(self.username.styleSheet())
        register_layout.addWidget(self.reg_username)
        
        self.reg_email = QLineEdit()
        self.reg_email.setPlaceholderText("Email")
        self.reg_email.setStyleSheet(self.username.styleSheet())
        register_layout.addWidget(self.reg_email)
        
        self.reg_password = QLineEdit()
        self.reg_password.setPlaceholderText("Password")
        self.reg_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.reg_password.setStyleSheet(self.username.styleSheet())
        register_layout.addWidget(self.reg_password)
        
        self.reg_confirm_password = QLineEdit()
        self.reg_confirm_password.setPlaceholderText("Confirm Password")
        self.reg_confirm_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.reg_confirm_password.setStyleSheet(self.username.styleSheet())
        register_layout.addWidget(self.reg_confirm_password)
        
        # Register button
        register_button = QPushButton("Register")
        register_button.setStyleSheet(login_button.styleSheet())
        register_button.clicked.connect(self.handle_register)
        register_layout.addWidget(register_button)
        
        # Login link
        login_link = QPushButton("Already have an account? Login")
        login_link.setStyleSheet(register_link.styleSheet())
        login_link.clicked.connect(lambda: self.stack.setCurrentWidget(login_page))
        register_layout.addWidget(login_link)
        
        register_layout.addStretch()
        
        # Add pages to stack
        self.stack.addWidget(login_page)
        self.stack.addWidget(register_page)

    def handle_login(self):
        """Handle the login process"""
        try:
            username = self.username.text().strip()
            password = self.password.text().strip()
            
            if not username or not password:
                QMessageBox.warning(self, "Login Error", "Please enter both username and password.")
                return
        
            # Set loading state
            self.set_loading(True)
            
            response = self.auth_api.login(username, password)
            
            if "error" in response:
                QMessageBox.warning(self, "Login Error", response["error"])
                return
        
            if "token" in response:
                self.auth_data = {
                    "token": response["token"],
                    "username": username
                }
                self.accept_login()
            else:
                QMessageBox.warning(self, "Login Error", "Login failed. Please try again.")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
        finally:
            # Reset loading state
            self.set_loading(False)

    def accept_login(self):
        """Process successful login and open main window"""
        if not hasattr(self, 'auth_data'):
            return
            
        try:
            self.main_window = MainWindow(
                token=self.auth_data['token'],
                username=self.auth_data['username']
            )
            self.main_window.show()
            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open main window: {str(e)}")
    def handle_register(self):
        username = self.reg_username.text()
        email = self.reg_email.text()
        password = self.reg_password.text()
        confirm_password = self.reg_confirm_password.text()
        
        if not all([username, email, password, confirm_password]):
            QMessageBox.warning(self, "Error", "Please fill in all fields")
            return
        
        if password != confirm_password:
            QMessageBox.warning(self, "Error", "Passwords do not match")
            return
        
        try:
            response = self.auth_api.register(username, email, password)
        
            if response and 'message' in response:
                QMessageBox.information(self, "Success", response['message'])
                self.stack.setCurrentIndex(0)  # Switch to login page
                # Clear registration fields
                self.reg_username.clear()
                self.reg_email.clear()
                self.reg_password.clear()
                self.reg_confirm_password.clear()
                # Pre-fill login username for convenience
                self.username.setText(username)
            elif response and 'error' in response:
                QMessageBox.warning(self, "Error", response['error'])
            else:
                QMessageBox.warning(self, "Error", "Registration failed. Please try again.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Registration failed: {str(e)}")
    
    
    
    def set_loading(self, is_loading):
        self.username.setDisabled(is_loading)
        self.password.setDisabled(is_loading)
        # Assuming login_button is accessible, otherwise store it as self.login_button
        # Disable or enable the login button
        for i in range(self.stack.currentWidget().layout().count()):
            item = self.stack.currentWidget().layout().itemAt(i).widget()
            if isinstance(item, QPushButton) and item.text() == "Login":
                item.setDisabled(is_loading)
                break