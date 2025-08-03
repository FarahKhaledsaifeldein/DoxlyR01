from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                            QPushButton, QFrame, QScrollArea, QGridLayout, QFileDialog, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from api.document_api import DocumentAPI
from api.project_api import ProjectAPI

class DashboardPage(QWidget):
    def __init__(self, token=None, username=None):
        super().__init__()
        self.username = username if username else "User"
        self.token = token
        self.document_api = DocumentAPI(token=token)
        self.init_ui()
        self.load_documents()  # Load documents after UI initialization
        
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

    def new_document(self):
        """Handle new document action"""
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Select Document")
        
        if file_path:
            try:
                # Upload the document
                response = self.document_api.upload_document(file_path)
                if response and isinstance(response, dict) and response.get('success', False):
                    QMessageBox.information(self, "Success", "Document uploaded successfully")
                    self.load_documents()  # Refresh the dashboard with correct method
                else:
                    QMessageBox.warning(self, "Error", "Failed to upload document")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to upload document: {str(e)}")

    def share_document(self):
        """Handle share document action"""
        try:
            # Get list of documents
            documents = self.document_api.get_documents()
            if documents:
                # Here you would typically show a dialog to select a document and user
                # For now, we'll just show a message
                QMessageBox.information(self, "Share Document", "Document sharing dialog would appear here")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to get documents: {str(e)}")

    def update_progress(self, value):
        """Update progress for document operations"""
        # You can implement this to show upload progress
        pass

    def load_documents(self):
        """Load and display documents"""
        try:
            print(f"Loading documents with token: {self.token}")  # Debug log
            documents = self.document_api.get_documents()
            print(f"Received documents: {documents}")  # Debug log
            
            if documents:
                # Update stats
                stats = {
                    "Total Documents": str(len(documents)),
                    "Recent Uploads": str(sum(1 for doc in documents if doc.get('is_recent', False))),
                    "Shared with me": str(sum(1 for doc in documents if doc.get('shared_with_me', False))),
                    "Active Projects": str(sum(1 for doc in documents if doc.get('is_active', False)))
                }
                
                # Find all QFrames that contain stat labels
                for frame in self.findChildren(QFrame):
                    # Get the title label from the frame
                    title_label = None
                    value_label = None
                    
                    # Find both labels in the frame
                    for label in frame.findChildren(QLabel):
                        if any(stat_title in label.text() for stat_title in stats.keys()):
                            title_label = label
                        else:
                            value_label = label
                    
                    # Update the value if we found matching labels
                    if title_label and value_label and title_label.text() in stats:
                        value_label.setText(stats[title_label.text()])
                        
        except Exception as e:
            error_msg = f"Failed to load documents: {str(e)}"
            print(f"Error: {error_msg}")  # Debug log
            QMessageBox.warning(self, "Error", error_msg)

    def init_ui(self):
        # Stats grid
        stats_grid = QGridLayout()
        stats_grid.setSpacing(7)
        
        stats_items = [
            {"title": "Total Documents", "value": "0", "color": "#89b4fa", "name": "total_documents"},
            {"title": "Recent Uploads", "value": "0", "color": "#f38ba8", "name": "recent_uploads"},
            {"title": "Shared with me", "value": "0", "color": "#fab387", "name": "shared_documents"},
            {"title": "Active Projects", "value": "0", "color": "#cba6f7", "name": "active_projects"}
        ]  # Added missing closing bracket here

    def handle_upload(self):
        """Handle document upload with additional inputs"""
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Document")
        if not file_path:
            return

        # Get document name
        document_name, ok = QInputDialog.getText(self, "Document Name", "Enter document name:")
        if not ok or not document_name.strip():
            QMessageBox.warning(self, "Input Required", "Document name is required.")
            return

        # Fetch projects for selection
        project_api = ProjectAPI()
        projects = project_api.get_projects(self.token)
        if isinstance(projects, dict) and 'error' in projects:
            QMessageBox.warning(self, "Error", f"Failed to fetch projects: {projects['error']}")
            return

        project_names = [proj.get('name', 'Unnamed Project') for proj in projects]
        project_ids = [proj.get('id') for proj in projects]

        selected_index, ok = QInputDialog.getItem(self, "Select Project", "Project:", project_names, 0, False)
        if not ok:
            return

        selected_project_id = None
        if selected_index in project_names:
            selected_project_id = project_ids[project_names.index(selected_index)]

        # Encryption flag dialog
        class EncryptionDialog(QDialog):
            def __init__(self, parent=None):
                super().__init__(parent)
                self.setWindowTitle("Encryption")
                self.is_encrypted = False
                layout = QVBoxLayout(self)
                self.checkbox = QCheckBox("Encrypt this document")
                layout.addWidget(self.checkbox)
                btn_box = QPushButton("OK")
                btn_box.clicked.connect(self.accept)
                layout.addWidget(btn_box)

            def accept(self):
                self.is_encrypted = self.checkbox.isChecked()
                super().accept()

        enc_dialog = EncryptionDialog(self)
        if enc_dialog.exec() != QDialog.DialogCode.Accepted:
            return
        is_encrypted_flag = enc_dialog.is_encrypted

        try:
            if not hasattr(self, 'document_api'):
                self.document_api = DocumentAPI(token=self.token)

            response = self.document_api.upload_document(
                file_path,
                name=document_name,
                project_id=selected_project_id,
                is_encrypted=is_encrypted_flag
            )

            if response and isinstance(response, dict) and response.get('success', False):
                QMessageBox.information(self, "Success", "Document uploaded successfully")
                self.load_dashboard_data()
            else:
                error_msg = response.get('error', 'Upload failed') if isinstance(response, dict) else 'Upload failed'
                QMessageBox.warning(self, "Error", error_msg)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Upload failed: {str(e)}")