import os
import requests
from datetime import datetime, timedelta
from typing import Optional
from .base_api import BaseAPI
from config import BACKEND_API_URL
from .auth_api import AuthAPI

class DocumentAPI:
    def __init__(self, token: Optional[str] = None, auth_api: Optional[AuthAPI] = None, expires_at: Optional[datetime] = None):
        self.base_url = f"{BACKEND_API_URL}documents/"
        self.expires_at = expires_at
        if token:
            self.auth_api = AuthAPI()
            self.auth_api.token = token
            self.auth_api.expires_at = expires_at or (datetime.now() + timedelta(seconds=7200))
        elif auth_api:
            self.auth_api = auth_api
        else:
            raise ValueError("Either token or auth_api must be provided")

    def get_headers(self) -> dict:
        return self.auth_api.get_auth_header()

    def upload_document(self, file_path: str, name: str = None, project_id: str = None, is_encrypted: bool = False) -> dict:
        """
        Upload a document to the server
        
        Args:
            file_path: Path to the file to upload
            name: Name of the document (optional)
            project_id: ID of the project to associate with (optional)
            is_encrypted: Whether the document is encrypted (default: False)
            
        Returns:
            dict: Response from the server
            
        Raises:
            Exception: If upload fails
        """
        url = f"{self.base_url}upload/"
        headers = self.get_headers()

        metadata = {
            "name": name or os.path.basename(file_path),
            "is_encrypted": str(is_encrypted).lower()
        }
        if project_id is not None:
            metadata["project_id"] = str(project_id)

        try:
            with open(file_path, "rb") as f:
                files = {"file": (os.path.basename(file_path), f)}
                response = requests.post(
                    url,
                    headers=headers,
                    files=files,
                    data=metadata,
                    timeout=30
                )
                response.raise_for_status()
                return response.json()
        except requests.exceptions.RequestException as e:
            print(f"[UPLOAD ERROR] RequestException: {e}")
            raise Exception(f"Connection error during upload: {str(e)}")
        except Exception as e:
            print(f"[UPLOAD ERROR] Exception: {e}")
            raise Exception(f"Upload failed: {str(e)}")

    def get_documents(self,params=None) -> dict:

        try:
            headers = self.get_headers()
            response = requests.get(
                f"{self.base_url}",
                headers=headers,
                params=params,
                timeout=10
            )
            print("Raw response text:", response.text)
            return self.handle_response(response)
        except Exception as e:
            print(f"Exception in get_documents: {str(e)}")
            raise Exception(f"Failed to fetch documents: {str(e)}")     
    
    def get_shared_documents(self) -> dict:
        try:
            headers = self.get_headers()
            response = requests.get(
                f"{self.base_url}shared/",
                headers=headers,
                timeout=10
            )
            return self.handle_response(response)
        except Exception as e:
            raise Exception(f"Failed to fetch shared documents: {str(e)}")

    def share_document(self, document_id: str, user_id: str) -> dict:
        try:
            headers = self.get_headers()
            response = requests.post(
                f"{self.base_url}{document_id}/share/",
                json={'user_id': user_id},
                headers=headers,
                timeout=10
            )
            return self.handle_response(response)
        except Exception as e:
            raise Exception(f"Failed to share document: {str(e)}")

    def handle_response(self, response) -> dict:
        try:
            if response.status_code == 401:
                raise Exception("Session expired. Please login again.")
            if not response.ok:
                print("RAW RESPONSE TEXT:", response.text)
                error_msg = response.json().get('error', response.text)
                raise Exception(f"API Error ({response.status_code}): {error_msg}")
            return response.json()
        except ValueError:
            print("FAILED TO PARSE JSON. RAW RESPONSE:", response.text)
            raise Exception("Invalid server response format")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Connection error: {str(e)}")