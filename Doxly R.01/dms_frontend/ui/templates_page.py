from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
                             QTableWidget, QTableWidgetItem, QFileDialog, QMessageBox,
                             QDialog, QFormLayout, QLineEdit, QComboBox, QTabWidget)
from PyQt6.QtCore import Qt
import os
import subprocess

class TemplatesPage(QWidget):
    def __init__(self, token=None, username=None):
        super().__init__()
        self.token = token
        self.username = username
        self.setup_ui()
        self.load_templates()
        
        # Register cleanup handler
        if hasattr(self.parent(), 'register_cleanup'):
            self.parent().register_cleanup(self.cleanup)
    
    def save_state(self):
        """Save the current state of the templates page"""
        return {
            'selected_rows': [item.row() for item in self.table.selectedItems()],
            'scroll_position': self.table.verticalScrollBar().value()
        }
    
    def restore_state(self, state):
        """Restore the saved state of the templates page"""
        if not state:
            return
            
        # Restore selected rows
        if 'selected_rows' in state:
            for row in state['selected_rows']:
                self.table.selectRow(row)
                
        # Restore scroll position
        if 'scroll_position' in state:
            self.table.verticalScrollBar().setValue(state['scroll_position'])
    
    def cleanup(self):
        """Cleanup resources when the page is closed"""
        # Clear any temporary files or resources
        self.table.clearSelection()
        self.table.setRowCount(0)
    
    def setup_ui(self):
        # Main layout
        # Set dark theme base style with enhanced transitions
        self.setStyleSheet("""
            /* Base theme */
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
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Header
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 10)
        
        title = QLabel("Templates")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #cdd6f4;")
        header_layout.addWidget(title)
        
        # Create new form button
        new_form_btn = QPushButton("Create New Form")
        new_form_btn.setStyleSheet("""
            QPushButton {
                background-color: #89b4fa;
                color: #1e1e2e;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #b4befe;
            }
        """)
        new_form_btn.clicked.connect(self.create_new_form)
        header_layout.addWidget(new_form_btn)
        
        main_layout.addWidget(header)
        
        # Templates table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Template Name", "Type", "Created By", "Last Modified", "Actions"])
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #1e1f22;
                border: 1px solid #313234;
                border-radius: 5px;
                gridline-color: #313234;
            }
            QHeaderView::section {
                background-color: #313244;
                color: #cdd6f4;
                padding: 8px;
                border: none;
                border-right: 1px solid #1e1f22;
            }
            QHeaderView::section:hover {
                background-color: #45475a;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #313234;
            }
            QTableWidget::item:hover {
                background-color: #383a40;
            }
            QTableWidget::item:selected {
                background-color: #45475a;
                border-radius: 3px;
            }
        """)
        main_layout.addWidget(self.table)
    
    def load_templates(self):
        # Sample data - in a real app, this would come from an API
        templates = [
            {"name": "Invoice Template", "type": "Excel", "created_by": "Admin", "last_modified": "2023-05-15"},
            {"name": "Contract Template", "type": "Word", "created_by": "Admin", "last_modified": "2023-06-20"},
            {"name": "Project Proposal", "type": "Word", "created_by": self.username, "last_modified": "2023-07-10"},
            {"name": "Budget Spreadsheet", "type": "Excel", "created_by": self.username, "last_modified": "2023-08-05"}
        ]
        
        self.table.setRowCount(len(templates))
        
        for i, template in enumerate(templates):
            self.table.setItem(i, 0, QTableWidgetItem(template["name"]))
            self.table.setItem(i, 1, QTableWidgetItem(template["type"]))
            self.table.setItem(i, 2, QTableWidgetItem(template["created_by"]))
            self.table.setItem(i, 3, QTableWidgetItem(template["last_modified"]))

            # Actions widget
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            
            edit_btn = QPushButton("Edit")
            edit_btn.setStyleSheet("""
                QPushButton {
                    background-color: #89b4fa;
                    color: #1e1e2e;
                    border: none;
                    padding: 5px 10px;
                    border-radius: 3px;
                    text-align: center;
                }
                QPushButton:hover {
                    background-color: #b4befe;
                }
            """)
            edit_btn.clicked.connect(lambda checked, t=template: self.edit_template(t))
            
            download_btn = QPushButton("Download")
            download_btn.setStyleSheet("""
                QPushButton {
                    background-color: #fab387;
                    color: #1e1e2e;
                    border: none;
                    padding: 5px 13px;
                    border-radius: 3px;
                    text-align: center;
                }
                QPushButton:hover {
                    background-color: #ffc9a0;
                }
            """)
            download_btn.clicked.connect(lambda checked, t=template: self.download_template(t))
            
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(download_btn)
            
            self.table.setCellWidget(i, 4, actions_widget)
    
    def create_new_form(self):
        dialog = FormCreationDialog(self)
        if dialog.exec():
            QMessageBox.information(self, "Success", "New form template created successfully!")
            self.load_templates()  # Refresh the templates list
    
    def edit_template(self, template):
        # Determine which application to open based on template type
        try:
            if template["type"] == "Word":
                # Open with Word
                subprocess.Popen(["start", "winword"], shell=True)
                QMessageBox.information(self, "Edit Template", f"Opening {template['name']} in Microsoft Word")
            elif template["type"] == "Excel":
                # Open with Excel
                subprocess.Popen(["start", "excel"], shell=True)
                QMessageBox.information(self, "Edit Template", f"Opening {template['name']} in Microsoft Excel")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not open the template: {str(e)}")
    
    def download_template(self, template):
        # Show file dialog to select download location
        file_dialog = QFileDialog()
        file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        
        # Set appropriate file extension based on template type
        if template["type"] == "Word":
            file_dialog.setNameFilter("Word Documents (*.docx)")
            file_dialog.setDefaultSuffix("docx")
        elif template["type"] == "Excel":
            file_dialog.setNameFilter("Excel Spreadsheets (*.xlsx)")
            file_dialog.setDefaultSuffix("xlsx")
        
        file_dialog.selectFile(template["name"])
        
        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                # In a real app, this would download the actual template file
                QMessageBox.information(self, "Download", f"Template '{template['name']}' downloaded successfully!")


class FormCreationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create New Form")
        self.setFixedWidth(500)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Form fields
        form_layout = QFormLayout()
        
        self.template_name = QLineEdit()
        self.template_type = QComboBox()
        self.template_type.addItems(["Word", "Excel"])
        self.template_category = QComboBox()
        self.template_category.addItems(["Contracts", "Invoices", "Reports", "Proposals", "Other"])
        
        form_layout.addRow("Template Name:", self.template_name)
        form_layout.addRow("Template Type:", self.template_type)
        form_layout.addRow("Category:", self.template_category)
        
        layout.addLayout(form_layout)
        
        # Tabs for different template creation options
        tabs = QTabWidget()
        
        # Create from scratch tab
        scratch_tab = QWidget()
        scratch_layout = QVBoxLayout(scratch_tab)
        
        create_scratch_btn = QPushButton("Create Blank Template")
        create_scratch_btn.clicked.connect(self.create_from_scratch)
        scratch_layout.addWidget(create_scratch_btn)
        scratch_layout.addStretch()
        
        # Upload existing tab
        upload_tab = QWidget()
        upload_layout = QVBoxLayout(upload_tab)
        
        upload_btn = QPushButton("Upload Existing File")
        upload_btn.clicked.connect(self.upload_existing)
        upload_layout.addWidget(upload_btn)
        self.selected_file_label = QLabel("No file selected")
        upload_layout.addWidget(self.selected_file_label)
        upload_layout.addStretch()
        
        # Add tabs
        tabs.addTab(scratch_tab, "Create New")
        tabs.addTab(upload_tab, "Upload Existing")
        
        layout.addWidget(tabs)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        save_btn = QPushButton("Save Template")
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(cancel_btn)
        
        layout.addLayout(buttons_layout)
    
    def create_from_scratch(self):
        if not self.template_name.text():
            QMessageBox.warning(self, "Error", "Please enter a template name")
            return
            
        try:
            # Open the appropriate application based on template type
            if self.template_type.currentText() == "Word":
                subprocess.Popen(["start", "winword"], shell=True)
            elif self.template_type.currentText() == "Excel":
                subprocess.Popen(["start", "excel"], shell=True)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not open application: {str(e)}")
    
    def upload_existing(self):
        file_dialog = QFileDialog()
        
        # Set filter based on selected template type
        if self.template_type.currentText() == "Word":
            file_dialog.setNameFilter("Word Documents (*.doc *.docx)")
        elif self.template_type.currentText() == "Excel":
            file_dialog.setNameFilter("Excel Spreadsheets (*.xls *.xlsx)")
        
        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                file_path = selected_files[0]
                file_name = os.path.basename(file_path)
                self.selected_file_label.setText(file_name)
                
                # If template name is empty, use the file name without extension
                if not self.template_name.text():
                    name_without_ext = os.path.splitext(file_name)[0]
                    self.template_name.setText(name_without_ext)