from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                            QPushButton, QFrame, QScrollArea, QGridLayout, QFileDialog, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from api.document_api import DocumentAPI  # Fixed import path

class DashboardPage(QWidget):
    def __init__(self, username=None, token=None):
        super().__init__()
        self.username = username if username else "User"
        self.token = token
        self.document_api = DocumentAPI(token=token)
        self.init_ui()
        self.load_dashboard_data()  # Load initial data
        
        # Register cleanup handler
        if hasattr(self.parent(), 'register_cleanup'):
            self.parent().register_cleanup(self.cleanup)
    
    def save_state(self):
        """Save the current state of the dashboard"""
        return {
            'scroll_position': self.findChild(QScrollArea).verticalScrollBar().value() if self.findChild(QScrollArea) else 0
        }
    
    def restore_state(self, state):
        """Restore the saved state of the dashboard"""
        if not state:
            return
            
        # Restore scroll position
        if 'scroll_position' in state:
            scroll_area = self.findChild(QScrollArea)
            if scroll_area:
                scroll_area.verticalScrollBar().setValue(state['scroll_position'])
    
    def cleanup(self):
        """Cleanup resources when the page is closed"""
        # Clear any cached data or temporary resources
        pass
    
    def init_ui(self):
        # Set dark theme base style
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1f22;
                color: #cdd6f4;
                font-family: Arial;
            }
            QFrame {
                background-color: #313244;
                border-radius: 5px;
            }
            QLabel {
                color: #cdd6f4;
            }
            QPushButton {
                background-color: #313244;
                color: #cdd6f4;
                border: none;
                padding: 8px 15px;
                border-radius: 5px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #45475a;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Stats grid
        stats_grid = QGridLayout()
        stats_grid.setSpacing(7)
        
        stats_items = [
            {"title": "Total Documents", "value": "0", "color": "#89b4fa"},
            {"title": "Recent Uploads", "value": "0", "color": "#f38ba8"},
            {"title": "Shared with me", "value": "0", "color": "#fab387"},
            {"title": "Active Projects", "value": "0", "color": "#cba6f7"}
        ]
        
        for i, item in enumerate(stats_items):
            stat_frame = QFrame()
            stat_frame.setStyleSheet(f"""
                background-color: {item['color']};
                border-radius: 5px;
                padding: 15px;
            """)
            stat_layout = QVBoxLayout(stat_frame)
            stat_layout.setSpacing(5)
            
            value_label = QLabel(item['value'])
            value_label.setStyleSheet("color: #1e1e2e; font-size: 24px; font-weight: bold;")
            value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            title_label = QLabel(item['title'])
            title_label.setStyleSheet("color: #1e1e2e; font-size: 14px;")
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            stat_layout.addWidget(value_label)
            stat_layout.addWidget(title_label)
            
            stats_grid.addWidget(stat_frame, i // 2, i % 2)
        
        layout.addLayout(stats_grid)
        
        # Quick actions
        quick_actions_frame = QFrame()
        quick_actions_frame.setStyleSheet("""
            QFrame {
                background-color: #313244;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        quick_actions_layout = QVBoxLayout(quick_actions_frame)
        
        title_label = QLabel("Quick Actions")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #cdd6f4;")
        quick_actions_layout.addWidget(title_label)
        
        # Create a container widget for the actions
        actions_container = QWidget()
        actions_layout = QHBoxLayout(actions_container)
        actions = [
            {"text": "New Document", "icon": "upload.png"},
            {"text": "Share Document", "icon": "project.png"},
            {"text": "Register", "icon": "share.png"},
            {"text": "Generate Report", "icon": "report.png"}
        ]
        
        for action in actions:
            btn = QPushButton(action['text'])
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #1e1f22;
                    border: 1px solid #45475a;
                    border-radius: 5px;
                    padding: 10px;
                    color: #cdd6f4;
                    font-size: 14px;
                    text-align: center;
                }
                QPushButton:hover {
                    background-color: #45475a;
                    border-color: #89b4fa;
                }
            """)
            # Connect button clicks to appropriate handlers
            if action['text'] == "New Document":
                # Change the button connection from self.new_document to self.handle_upload
                btn.clicked.connect(self.handle_upload)
            elif action['text'] == "Share Document":
                btn.clicked.connect(self.share_document)
            elif action['text'] == "Register":
                btn.clicked.connect(self.register_document)
            elif action['text'] == "Generate Report":
                btn.clicked.connect(self.generate_report)
            actions_layout.addWidget(btn)
        
        quick_actions_layout.addWidget(actions_container)
        layout.addWidget(quick_actions_frame)
        
        # Recent activity
        activity_frame = QFrame()
        activity_frame.setStyleSheet("""
            QFrame {
                background-color: #313244;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        activity_layout = QVBoxLayout(activity_frame)
        
        activity_title = QLabel("Recent Activity")
        activity_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #cdd6f4;")
        activity_layout.addWidget(activity_title)
        
        # Placeholder for activity list
        activity_list = QFrame()
        activity_list.setStyleSheet("""
            QFrame {
                background-color: #1e1f22;
                border-radius: 5px;
                padding: 15px;
            }
        """)
        activity_list_layout = QVBoxLayout(activity_list)
        
        placeholder_label = QLabel("No recent activity")
        placeholder_label.setStyleSheet("color: #6c7086; font-size: 14px;")
        placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        activity_list_layout.addWidget(placeholder_label)
        
        activity_layout.addWidget(activity_list)
        layout.addWidget(activity_frame)
        
        # Add stretch to push everything to the top
        layout.addStretch()
    
    def handle_upload(self):
        """Handle document upload"""
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Document")
        if file_path:
            try:
                # Initialize document API if not already done
                if not hasattr(self, 'document_api'):
                    self.document_api = DocumentAPI(token=self.token)
                    
                # Upload the document
                success = self.document_api.upload_document(file_path)
                
                if success:
                    QMessageBox.information(self, "Success", "Document uploaded successfully")
                    self.load_dashboard_data()  # Refresh the dashboard
                else:
                    QMessageBox.warning(self, "Error", "Failed to upload document")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Upload failed: {str(e)}")
    
    def load_dashboard_data(self):
        """Load and update dashboard data"""
        try:
            if not hasattr(self, 'document_api'):
                self.document_api = DocumentAPI(token=self.token)
                
            documents = self.document_api.get_documents()
            print(f"Received documents: {documents}")  # Add this debug line
            
            # Update stats
            total_docs = len(documents) if documents else 0
            print(f"Total documents count: {total_docs}")  # Add this debug line
            
            recent_uploads = sum(1 for doc in documents if doc.get('is_recent', False)) if documents else 0
            shared_docs = sum(1 for doc in documents if doc.get('shared_with_me', False)) if documents else 0
            active_projects = sum(1 for doc in documents if doc.get('is_active', False)) if documents else 0
            
            # Find and update stat labels
            for frame in self.findChildren(QFrame):
                value_label = None
                title_label = None
                
                # First find both labels in the frame
                for label in frame.findChildren(QLabel):
                    if any(stat_title in label.text() for stat_title in ["Total Documents", "Recent Uploads", "Shared with me", "Active Projects"]):
                        title_label = label
                    else:
                        value_label = label
                
                # Now update the value if we found matching labels
                if title_label and value_label:
                    if "Total Documents" in title_label.text():
                        value_label.setText(str(total_docs))
                    elif "Recent Uploads" in title_label.text():
                        value_label.setText(str(recent_uploads))
                    elif "Shared with me" in title_label.text():
                        value_label.setText(str(shared_docs))
                    elif "Active Projects" in title_label.text():
                        value_label.setText(str(active_projects))
                        
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load dashboard data: {str(e)}")

    def share_document(self):
        """Handle document sharing"""
        QMessageBox.information(self, "Share Document", "Document sharing feature coming soon!")
        
    def register_document(self):
        """Handle document registration"""
        QMessageBox.information(self, "Register", "Document registration feature coming soon!")
        
    def generate_report(self):
        """Handle report generation"""
        QMessageBox.information(self, "Generate Report", "Report generation feature coming soon!")
