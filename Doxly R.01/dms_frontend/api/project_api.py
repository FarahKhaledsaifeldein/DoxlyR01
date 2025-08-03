import requests
from datetime import datetime, timedelta
from typing import Optional
from config import BACKEND_API_URL
from .base_api import BaseAPI
from .auth_api import AuthAPI
from .document_api import DocumentAPI

class ProjectAPI(BaseAPI):
    def __init__(self, token: str, expires_at: Optional[datetime] = None):
        super().__init__()
        self.token = token
        self.expires_at = expires_at or (datetime.now() + timedelta(seconds=7200))  # Default to 2 hours
        self.set_token(token)
        self.document_api = DocumentAPI(auth_api=AuthAPI())  # Initialize DocumentAPI

    def is_token_valid(self) -> bool:
        return self.token and datetime.now() < self.expires_at

    def get_headers(self) -> dict:
        if not self.is_token_valid():
            raise Exception("Session expired. Please login again.")
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    def get_projects(self, user_id: Optional[str] = None) -> dict:
        """Get all projects for authenticated user"""
        try:
            headers = self.get_headers()
            params = {}
            if user_id:
                params['user_id'] = user_id
            response = requests.get(
                f"{self.base_url}projects/",
                headers=headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 401:
                raise Exception("Session expired. Please login again.")
            if not response.ok:
                raise Exception(f"Failed to fetch projects: {response.text}")
                
            return response.json()
            
        except Exception as e:
            raise Exception(f"Error fetching projects: {str(e)}")

    def create_project(self, project_data: dict, document_data: dict = None) -> dict:
        """Create a new project with optional document upload"""
        try:
            headers = self.get_headers()
            response = requests.post(
                f"{self.base_url}projects/",
                json=project_data,
                headers=headers
            )
            response.raise_for_status()
            project_result = response.json()

            if document_data:
                print("Document data:", document_data)
                project_id = project_result.get("id")
                if not project_id:
                    return {"error": "Project created but no project ID returned for document upload"}

                document_data = document_data.copy()
                document_data["project_id"] = document_data.get("project_id", project_id)

                document_result = self.document_api.upload_document(
                    file_path=document_data["file_path"],
                    name=document_data.get("name"),
                    project_id=document_data["project_id"],
                    is_encrypted=document_data.get("is_encrypted", False)
                )
                print("Debug: Document upload result:", document_result)
                return {"project": project_result, "document": document_result}

            return project_result

        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code
            print("HTTP Error response:", e.response.text)
            if status_code == 400:
                try:
                    error_data = e.response.json()
                    return {"error": error_data.get('error', "Invalid project data")}
                except ValueError:
                    return {"error": "Invalid project data (non-JSON response)"}
            elif status_code == 401:
                return {"error": "Unauthorized access"}
            else:
                return {"error": f"Failed to create project. Status code: {status_code}"}
        except requests.exceptions.RequestException as e:
            print("Connection error:", str(e))
            return {"error": f"Connection error: {str(e)}"}
        except ValueError:
            return {"error": "Invalid JSON response from server"}