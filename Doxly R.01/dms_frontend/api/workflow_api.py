from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from api.workflow_api import WorkflowAPI

class WorkflowsScreen(QWidget):
    def __init__(self, token):
        super().__init__()

        # Set window properties
        self.setWindowTitle("Workflows - Doxly")
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()

        # Label to display workflow data
        self.workflows_label = QLabel("Fetching Workflows...")
        layout.addWidget(self.workflows_label)

        # Button to refresh workflow list
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.load_workflows)
        layout.addWidget(self.refresh_btn)

        self.setLayout(layout)

        # Store user token
        self.token = token
        self.api = WorkflowAPI()  # Create instance of WorkflowAPI
        self.load_workflows()

    def load_workflows(self):
        """Fetch and display workflows"""
        workflows = self.api.get_workflows(self.token)  # Call class method
        workflow_names = "\n".join([wf["name"] for wf in workflows])
        self.workflows_label.setText(f"Workflows:\n{workflow_names}")
