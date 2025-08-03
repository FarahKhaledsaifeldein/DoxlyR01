from collections import UserList
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QTableWidget, QTableWidgetItem, QLabel, QFileDialog,
                            QProgressBar, QMessageBox, QFrame, QTabWidget,
                            QLineEdit, QDialog, QFormLayout, QComboBox)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap
from api.document_api import DocumentAPI
from api.project_api import ProjectAPI
import os
from PyQt6 import sip
import requests
from datetime import datetime


class UploadDialog(QDialog):
    def __init__(self, token, file_path, parent=None):
        super().__init__(parent)
        self.token = token
        self.file_path = file_path
        self.setWindowTitle("Upload Document")
        self.layout = QFormLayout(self)

        # Set name input to filename (without extension) by default
        file_name = os.path.basename(file_path)
        base_name = os.path.splitext(file_name)[0]
        self.name_input = QLineEdit(self)
        self.name_input.setText(base_name)
        self.layout.addRow("Document Name:", self.name_input)

        self.project_api = ProjectAPI(token)
        self.project_combo = QComboBox(self)
        projects = self.project_api.get_projects()
        if isinstance(projects, dict) and 'error' in projects:
            self.project_combo.addItem("Default Project", None)
        else:
            self.project_combo.addItem("Default Project", None)  # Default option
            for project in projects:
                self.project_combo.addItem(project.get('name', 'Unknown'), project.get('id'))
        self.layout.addRow("Project:", self.project_combo)

        self.encrypt_check = QPushButton("Encrypt Document")
        self.encrypt_check.setCheckable(True)
        self.layout.addRow(self.encrypt_check)

        self.button_box = QHBoxLayout()
        self.ok_button = QPushButton("Upload")
        self.cancel_button = QPushButton("Cancel")
        self.button_box.addWidget(self.ok_button)
        self.button_box.addWidget(self.cancel_button)
        self.layout.addRow(self.button_box)

        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

    def get_values(self):
        return {
            'name': self.name_input.text() or None,
            'project_id': self.project_combo.currentData(),
            'is_encrypted': self.encrypt_check.isChecked()
        }


class DocumentPage(QWidget):
    def __init__(self, token=None, username=None, expires_at=None):
        super().__init__()
        print(f"Debug: Initializing DocumentPage with token: {token[:10] if token else None}")
        self.token = token
        self.username = username if username else "User"
        
        # Handle expires_at conversion
        if isinstance(expires_at, str):
            expires_at_dt = datetime.fromisoformat(expires_at)
        else:
            expires_at_dt = expires_at
            
        self.document_api = DocumentAPI(token=token, expires_at=expires_at_dt)
        self.current_filter = "All"
        self._progress_visible = False
        
        # Initialize search timer
        self.search_timer = QTimer(self)
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self._perform_search)
        
        self.setup_ui()
        self.load_documents()

    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(20, 20, 20, 20)

        # Header section
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)

        # Left side (title + filters)
        left_side = QWidget()
        left_layout = QVBoxLayout(left_side)
        left_layout.setSpacing(10)

        title = QLabel("Project files")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #cdd6f4;")
        left_layout.addWidget(title)

        # Filter buttons
        filter_container = QWidget()
        filter_layout = QHBoxLayout(filter_container)
        filter_layout.setSpacing(10)
        self.filter_buttons = {}
        for filter_text in ["All", "Documents", "Spreadsheets", "PDFs", "Images"]:
            filter_btn = QPushButton(filter_text)
            filter_btn.setCheckable(True)
            filter_btn.setChecked(filter_text == "All")
            filter_btn.clicked.connect(lambda checked, text=filter_text: self.apply_filter(text))
            filter_btn.setStyleSheet("""
                QPushButton {
                    background-color: #313244;
                    color: #cdd6f4;
                    border: none;
                    padding: 5px 15px;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #45475a;
                }
                QPushButton:checked {
                    background-color: #89b4fa;
                    color: #1e1e2e;
                }
            """)
            filter_layout.addWidget(filter_btn)
            self.filter_buttons[filter_text] = filter_btn
        left_layout.addWidget(filter_container)
        header_layout.addWidget(left_side)

        # Right side (search + upload)
        right_side = QWidget()
        right_layout = QHBoxLayout(right_side)
        right_layout.setSpacing(10)

        # Search box
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search files...")
        self.search_box.textChanged.connect(self._on_search_changed)
        self.search_box.setStyleSheet("""
            QLineEdit {
                background-color: #313244;
                color: #cdd6f4;
                border: none;
                padding: 8px;
                border-radius: 5px;
                min-width: 200px;
            }
        """)
        right_layout.addWidget(self.search_box)

        # Upload button
        new_doc_btn = QPushButton("+ New document")
        new_doc_btn.setStyleSheet("""
            QPushButton {
                background-color: #89b4fa;
                color: #1e1e2e;
                border: none;
                padding: 8px 15px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #b4befe;
            }
        """)
        new_doc_btn.clicked.connect(self.handle_upload)
        right_layout.addWidget(new_doc_btn)
        header_layout.addWidget(right_side)
        content_layout.addWidget(header)

        # Documents table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["File name", "Type", "Size", "Uploaded by", "Last modified", "Actions"])
        header = self.table.horizontalHeader()
        if header:
            header.setStretchLastSection(True)
        content_layout.addWidget(self.table)

        # Progress bar
        self.progress_container = QFrame()
        progress_layout = QVBoxLayout(self.progress_container)
        progress_layout.setContentsMargins(0, 0, 0, 0)
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        progress_layout.addWidget(self.progress)
        content_layout.addWidget(self.progress_container)

        main_layout.addWidget(content)

    def _on_search_changed(self):
        """Debounce search input"""
        if hasattr(self, 'search_timer'):
            self.search_timer.start(300)  # 300ms delay

    def _perform_search(self):
        """Execute search with current filter"""
        if hasattr(self, 'search_box') and not sip.isdeleted(self.search_box):
            search_text = self.search_box.text().strip()
            self.load_documents(search_text)

    def load_documents(self, search_text=None):
        """Load documents from API with optional search"""
        try:
            self.show_progress(0)
            print(f"Debug: Loading documents with token: {self.token[:10]}...")
            
            # Call API without params argument
            documents = self.document_api.get_documents()
            
            if isinstance(documents, dict) and 'error' in documents:
                raise Exception(documents['error'])
                
            # Filter locally if search_text is provided
            if search_text:
                search_text = search_text.lower()
                documents = [doc for doc in documents if search_text in doc.get('name', '').lower()]
                
            self._populate_table(documents)
            
        except Exception as e:
            print(f"Debug: Error in load_documents: {str(e)}")
            if not sip.isdeleted(self):
                QMessageBox.warning(self, "Error", f"Failed to load documents: {str(e)}")
        finally:
            self.show_progress(100)
            self.hide_progress()

    def _populate_table(self, documents):
        """Populate table with API response"""
        self.table.setRowCount(0)
        
        if not documents:
            self.table.setRowCount(1)
            no_docs_item = QTableWidgetItem("No documents found")
            no_docs_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(0, 0, no_docs_item)
            self.table.setSpan(0, 0, 1, 6)
            return
            
        for row, doc in enumerate(documents):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(doc.get('name', '')))
            self.table.setItem(row, 1, QTableWidgetItem(doc.get('type', '')))
            self.table.setItem(row, 2, QTableWidgetItem(self.format_size(doc.get('size', 0))))
            self.table.setItem(row, 3, QTableWidgetItem(doc.get('owner', '')))
            self.table.setItem(row, 4, QTableWidgetItem(doc.get('modified', '')))
            
            # Actions column
            actions = QWidget()
            actions_layout = QHBoxLayout(actions)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            
            download_btn = QPushButton("Download")
            download_btn.clicked.connect(lambda _, d=doc: self.handle_download(d))
            actions_layout.addWidget(download_btn)
            
            delete_btn = QPushButton("Delete")
            delete_btn.clicked.connect(lambda _, d=doc: self.handle_delete(d))
            actions_layout.addWidget(delete_btn)
            
            self.table.setCellWidget(row, 5, actions)

    def apply_filter(self, filter_type):
        """Apply filter to currently loaded documents"""
        self.current_filter = filter_type
        if hasattr(self, 'filter_buttons'):
            for btn_text, btn in self.filter_buttons.items():
                if not sip.isdeleted(btn):
                    btn.setChecked(btn_text == filter_type)
        self.filter_documents()

    def filter_documents(self):
        """Filter documents in the table"""
        try:
            search_text = ''
            if hasattr(self, 'search_box') and not sip.isdeleted(self.search_box):
                search_text = self.search_box.text().lower()
            if not hasattr(self, 'table') or sip.isdeleted(self.table):
                return
                
            current_selection = [item.row() for item in self.table.selectedItems()]
            scroll_position = self.table.verticalScrollBar().value()
            
            for row in range(self.table.rowCount()):
                if sip.isdeleted(self.table):
                    return
                    
                item = self.table.item(row, 0)
                type_item = self.table.item(row, 1)
                
                if item and type_item:
                    file_name = item.text().lower()
                    file_type = type_item.text()
                    type_matches = (self.current_filter == "All" or 
                                   file_type.startswith(self.current_filter.rstrip('s')))
                    search_matches = not search_text or search_text in file_name
                    
                    if not sip.isdeleted(self.table):
                        self.table.setRowHidden(row, not (type_matches and search_matches))
            
            if not sip.isdeleted(self.table):
                for row in current_selection:
                    self.table.selectRow(row)
                self.table.verticalScrollBar().setValue(scroll_position)
                
        except Exception as e:
            print(f"[DEBUG] Error in filter_documents: {str(e)}")

    def format_size(self, size_in_bytes):
        """Format file size in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_in_bytes < 1024:
                return f"{size_in_bytes:.1f} {unit}"
            size_in_bytes /= 1024
        return f"{size_in_bytes:.1f} TB"

    def refresh_documents(self):
        """Refresh documents from API"""
        try:
            documents = self.document_api.get_documents()
            if isinstance(documents, dict) and 'error' in documents:
                raise Exception(documents['error'])
            self.load_documents()
        except Exception as e:
            QMessageBox.warning(self, "Refresh Error", str(e))

    def test_auth(self):
        """Test authentication by making a simple API request"""
        try:
            headers = self.document_api.get_headers()
            response = requests.get(
                f"{self.document_api.base_url}documents/",
                headers=headers,
                timeout=5
            )
            print("Auth test response:", response.status_code, response.text)
            return response.status_code == 200
        except Exception as e:
            print("Auth test failed:", str(e))
            return False

    def handle_upload(self):
        """Handle document upload"""
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Document")
        if not file_path:
            return

        dialog = UploadDialog(self.token, file_path, self)
        if not dialog.exec():
            return

        values = dialog.get_values()
        try:
            self.show_progress(0)
            
            # Debug: Print upload parameters
            print(f"Uploading file: {file_path}")
            print(f"With parameters: {values}")
            
            # Make the API call
            response = self.document_api.upload_document(
                file_path,
                name=values['name'],
                project_id=values['project_id'],
                is_encrypted=values['is_encrypted']
            )
            
            # Debug: Print raw response
            print(f"Raw API response: {response}")
            
            # Handle response
            if isinstance(response, dict):
                if 'error' in response:
                    raise Exception(response['error'])
                    
                self.show_progress(100)
                QMessageBox.information(self, "Success", "Document uploaded successfully")
                self.refresh_documents()
                return
                
            elif isinstance(response, requests.Response):
                response.raise_for_status()  # Raise exception for bad status codes
                
                if response.status_code == 201:
                    self.show_progress(100) 
                    QMessageBox.information(self, "Success", "Document uploaded successfully")
                    self.refresh_documents()
                    return
                    
            else:
                raise Exception("Invalid response format from server")
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Network error: {str(e)}"
            print(f"Upload exception: {error_msg}")
            QMessageBox.critical(self, "Error", f"Upload failed: {error_msg}")
            
        except Exception as e:
            error_msg = str(e)
            print(f"Upload exception: {error_msg}")
            QMessageBox.critical(self, "Error", f"Upload failed: {error_msg}")
            
        finally:
            self.show_progress(100)
            self.hide_progress()

    def handle_share(self, document):
        """Handle document sharing"""
        doc_name = getattr(document, 'name', 'Unknown document')
        QMessageBox.information(self, "Share", f"Sharing document: {doc_name}")

    def handle_download(self, document):
        """Handle document download"""
        try:
            success = True  # Temporary for testing
            if success:
                QMessageBox.information(self, "Success", "Document downloaded successfully")
            else:
                QMessageBox.warning(self, "Error", "Failed to download document")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Download failed: {str(e)}")

    def handle_delete(self, document):
        """Handle document deletion"""
        doc_name = getattr(document, 'name', 'Unknown document')
        reply = QMessageBox.question(self, "Confirm Delete", 
                                    f"Are you sure you want to delete {doc_name}?", 
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            try:
                success = True  # Temporary for testing
                if success:
                    QMessageBox.information(self, "Success", "Document deleted successfully")
                    self.load_documents()
                else:
                    QMessageBox.warning(self, "Error", "Failed to delete document")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Delete failed: {str(e)}")

    def show_progress(self, value=0):
        """Show progress bar"""
        if hasattr(self, 'progress') and not sip.isdeleted(self.progress):
            self._progress_visible = True
            self.progress.setVisible(True)
            self.progress.setValue(value)

    def hide_progress(self):
        """Hide progress bar"""
        if hasattr(self, 'progress') and not sip.isdeleted(self.progress):
            self._progress_visible = False
            self.progress.setVisible(False)

    def save_state(self):
        """Save current UI state"""
        state = {
            'current_filter': self.current_filter,
            'search_text': '',
            'selected_rows': [],
            'scroll_position': 0,
            'progress_visible': self._progress_visible
        }
        
        if hasattr(self, 'search_box') and not sip.isdeleted(self.search_box):
            state['search_text'] = self.search_box.text()
            
        if hasattr(self, 'table') and not sip.isdeleted(self.table):
            state['selected_rows'] = [item.row() for item in self.table.selectedItems()]
            state['scroll_position'] = self.table.verticalScrollBar().value()
            
        return state

    def restore_state(self, state):
        """Restore UI state from saved data"""
        if not state:
            return
            
        if 'current_filter' in state:
            self.apply_filter(state['current_filter'])
            
        if 'search_text' in state and hasattr(self, 'search_box') and not sip.isdeleted(self.search_box):
            self.search_box.setText(state['search_text'])
            self._perform_search()  # Changed from search_documents
            
        if hasattr(self, 'table') and not sip.isdeleted(self.table):
            if 'selected_rows' in state:
                for row in state['selected_rows']:
                    if row < self.table.rowCount():
                        self.table.selectRow(row)
            if 'scroll_position' in state:
                self.table.verticalScrollBar().setValue(state['scroll_position'])
                
        if 'progress_visible' in state:
            if state['progress_visible']:
                self.show_progress()
            else:
                self.hide_progress()

    def cleanup(self):
        """Clean up resources"""
        if hasattr(self, 'table'):
            self.table.clearSelection()
            self.table.setRowCount(0)
        if hasattr(self, 'search_box'):
            self.search_box.clear()
        self.current_filter = "All"
        self.hide_progress()

    def closeEvent(self, event):
        """Handle window close event"""
        self.cleanup()
        super().closeEvent(event)

    def hideEvent(self, event):
        """Handle window hide event"""
        if self._progress_visible and hasattr(self, 'progress') and not sip.isdeleted(self.progress):
            self._progress_visible = False
            self.progress.setVisible(False)
        super().hideEvent(event)

    def showEvent(self, event):
        """Handle window show event"""
        if self._progress_visible and hasattr(self, 'progress') and not sip.isdeleted(self.progress):
            self.progress.setVisible(True)
        super().showEvent(event)


def login_and_get_token(username, password):
    """Helper function to login and get token"""
    login_url = "http://localhost:8000/api/token/"
    response = requests.post(login_url, data={"username": username, "password": password})
    if response.status_code == 200:
        tokens = response.json()
        return tokens["access"]  # Store this token
    else:
        raise Exception(f"Login failed: {response.status_code} - {response.text}")


def upload_document(file_path, token, name=None, project_id=None, is_encrypted=False):
    """Standalone function to upload document"""
    url = "http://localhost:8000/api/documents/upload/"
    headers = {"Authorization": f"Token {token}"}

    metadata = {
        "name": name or "",
        "project_id": str(project_id) if project_id is not None else "",
        "is_encrypted": str(is_encrypted).lower(),
    }

    try:
        with open(file_path, "rb") as f:
            files = {"file": (file_path, f)}
            response = requests.post(url, headers=headers, files=files, data=metadata)

        if response.status_code == 201:
            return response.json()
        else:
            raise Exception(f"Upload failed: {response.status_code} - {response.text}")
    except Exception as e:
        raise Exception(f"Exception during upload: {str(e)}")