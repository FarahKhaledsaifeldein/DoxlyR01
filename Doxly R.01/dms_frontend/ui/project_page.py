from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QTableWidget, QTableWidgetItem, QLabel, QDialog,
                             QLineEdit, QFormLayout, QMessageBox)
from PyQt6.QtCore import Qt
from api.project_api import ProjectAPI
import requests 

class ProjectPage(QWidget):
    def __init__(self, token=None, username=None):
        super().__init__()
        self.token = token
        self.project_api = ProjectAPI(token)  # Pass token here
        self.username = username
        self.setup_ui()
        self.load_projects()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Header section
        header = QWidget()
        header_layout = QHBoxLayout(header)
        
        title = QLabel("Projects")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50;")
        header_layout.addWidget(title)
        
        new_project_btn = QPushButton("New Project")
        new_project_btn.setStyleSheet("""
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
        new_project_btn.clicked.connect(self.show_new_project_dialog)
        header_layout.addWidget(new_project_btn)
        
        layout.addWidget(header)
        
        # Projects table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Name", "Code", "Trade", "Sub-Trade", "Created By", "Actions"])
    
        self.table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                background-color:  #bdc3c7;
            }
            QHeaderView::section {
                background-color:  #bdc3c7;
                color: black;
                padding: 8px;
                border: none;
            }
        """)
        layout.addWidget(self.table)
    
    def load_projects(self):
        try:
            if not self.token:
                print("Debug: Token is missing")
                QMessageBox.warning(self, "Error", "Authentication token not found. Please log in again.")
                return
                
            print(f"Debug: Making API call with token: {self.token[:5]}...")
            response = self.project_api.get_projects(self.token)
            print(f"Debug: API Response: {response}")
            
            if isinstance(response, dict) and 'error' in response:
                print(f"Debug: Error response: {response['error']}")
                QMessageBox.warning(self, "Error", str(response['error']))
                return
                
            if not isinstance(response, list):
                QMessageBox.warning(self, "Error", "Invalid response format from server")
                return
                
            projects = response
            self.table.setRowCount(len(projects))
            
            for i, project in enumerate(projects):
                if not isinstance(project, dict):
                    continue
                        
                # Create items with light text color
                name_item = QTableWidgetItem(str(project.get('name', '')))
                name_item.setForeground(Qt.GlobalColor.black)  # Set text color to black
                
                code_item = QTableWidgetItem(str(project.get('code', '')))
                code_item.setForeground(Qt.GlobalColor.black)
                
                trade_item = QTableWidgetItem(str(project.get('trade', '')))
                trade_item.setForeground(Qt.GlobalColor.black)
                
                sub_trade_item = QTableWidgetItem(str(project.get('sub_trade', '')))
                sub_trade_item.setForeground(Qt.GlobalColor.black)
                
                created_by_item = QTableWidgetItem(str(project.get('created_by', '')))
                created_by_item.setForeground(Qt.GlobalColor.black)
                
                self.table.setItem(i, 0, name_item)
                self.table.setItem(i, 1, code_item)
                self.table.setItem(i, 2, trade_item)
                self.table.setItem(i, 3, sub_trade_item)
                self.table.setItem(i, 4, created_by_item)
                
                actions = QWidget()
                actions_layout = QHBoxLayout(actions)
                actions_layout.setContentsMargins(0, 0, 0, 0)
                
                view_btn = QPushButton("View")
                view_btn.clicked.connect(lambda checked, p=project: self.handle_view_project(p))
                actions_layout.addWidget(view_btn)
                
                edit_btn = QPushButton("Edit")
                edit_btn.clicked.connect(lambda checked, p=project: self.handle_edit_project(p))
                actions_layout.addWidget(edit_btn)
                
                self.table.setCellWidget(i, 5, actions)

        except Exception as e:
            print(f"Debug: Exception occurred: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to load projects: {str(e)}")

    def show_new_project_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("New Project")
        dialog.setFixedWidth(400)
        
        layout = QFormLayout(dialog)
        
        # Project form fields
        name_input = QLineEdit()
        code_input = QLineEdit()
        trade_input = QLineEdit()
        sub_trade_input = QLineEdit()
        abbreviation_input=QLineEdit()
        
        layout.addRow("Name:", name_input)
        layout.addRow("Code:", code_input)
        layout.addRow("Trade:", trade_input)
        layout.addRow("Sub-Trade:", sub_trade_input)
        layout.addRow("abbreviation", abbreviation_input)
        
        # Buttons
        buttons = QHBoxLayout()
        create_btn = QPushButton("Create")
        cancel_btn = QPushButton("Cancel")
        
        create_btn.clicked.connect(lambda: self.handle_create_project(
            dialog,
            name_input.text(),
            code_input.text(),
            trade_input.text(),
            sub_trade_input.text(),
            abbreviation_input.text(),

        ))
        cancel_btn.clicked.connect(dialog.reject)
        
        buttons.addWidget(create_btn)
        buttons.addWidget(cancel_btn)
        layout.addRow(buttons)
        
        dialog.exec()
    
    def handle_create_project(self, dialog, name, code, trade, sub_trade,abbreviation):
        if not all([name, code]):
            QMessageBox.warning(self, "Error", "Please fill in all required fields")
            return
        
        try:
            if not self.token:
                QMessageBox.warning(self, "Error", "Authentication token not found. Please log in again.")
                return
            
            project_data = {
                "name": name,
                "code": code,
                "trade": trade if trade else None,
                "sub_trade": sub_trade if sub_trade else None,
                "abbreviation": abbreviation if abbreviation else None
            }
            print("DEBUG - project_data to send:", project_data)

            # Make API call with proper headers
            headers = {
                'Authorization': f'Bearer {self.token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                "http://localhost:8000/api/projects/",  # Update with your actual API URL
                json=project_data,
                headers=headers
            )
            
            # Handle response
            if response.status_code == 201:
                dialog.accept()
                QMessageBox.information(self, "Success", "Project created successfully")
                self.load_projects()
                return
            
            # Handle specific error cases
            try:
                error_data = response.json()
                error_msg = error_data.get('detail') or str(error_data)
            except ValueError:
                error_msg = f"Server returned {response.status_code}"
                
            QMessageBox.warning(self, "Error", f"Failed to create project: {error_msg}")
            
        except Exception as e:
            if "folder_path" in str(e):
               QMessageBox.critical(self, "Error", "Project creation failed due to server configuration")
            else:
                 QMessageBox.critical(self, "Error", f"Project creation failed: {str(e)}")
           
    def handle_view_project(self, project):
        # TODO: Implement project viewing logic
        QMessageBox.information(self, "View", f"Viewing project: {project.name}")
    
    def handle_edit_project(self, project):
        # TODO: Implement project editing logic
        QMessageBox.information(self, "Edit", f"Editing project: {project.name}")