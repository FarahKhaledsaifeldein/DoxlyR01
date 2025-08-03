""""
Fixed API Client for connecting to Django REST Backend
"""

import requests
import json
import logging
from PyQt6.QtCore import QObject, pyqtSignal, QThread

logger = logging.getLogger(__name__)

class APIClient(QObject):
    """Client for communicating with the Doxly Django REST backend API"""
    
    # Define signals for async operations
    request_finished = pyqtSignal(dict)
    request_error = pyqtSignal(str)
    auth_error = pyqtSignal()
    
    def __init__(self, base_url="http://localhost:8000/api/"):
        """Initialize the API client with base URL and auth token"""
        super().__init__()
        self.base_url = base_url
        self.session = requests.Session()
        self.token = None
        
    def set_token(self, token):
        """Set the authentication token for API requests"""
        self.token = token
        if token:
            self.session.headers.update({'Authorization': f'Bearer {token}'})
        else:
            if 'Authorization' in self.session.headers:
                del self.session.headers['Authorization']
    
    def _make_request(self, method, endpoint, data=None, params=None, files=None):
        """Make HTTP request to the API with error handling"""
        url = f"{self.base_url}{endpoint}"
        
        # Set up headers with authentication
        headers = {}
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'
            
        # For debugging
        logger.debug(f"Making {method} request to {url}")
        if data:
            logger.debug(f"Request data: {data}")
            
        try:
            if method.lower() == 'get':
                response = self.session.get(url, params=params, headers=headers)
            elif method.lower() == 'post':
                response = self.session.post(url, json=data, headers=headers, files=files)
            elif method.lower() == 'put':
                response = self.session.put(url, json=data, headers=headers)
            elif method.lower() == 'delete':
                response = self.session.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
                
            logger.debug(f"Response status: {response.status_code}")
            
            # Check for authentication errors
            if response.status_code == 401:
                logger.error("Authentication failed")
                self.auth_error.emit()
                return None
                
            response.raise_for_status()
            
            # Parse JSON response if content exists
            if response.content:
                try:
                    result = response.json()
                    logger.debug(f"Response data: {result}")
                    return result
                except json.JSONDecodeError:
                    logger.error("Failed to decode JSON response")
                    return {"error": "Invalid JSON response"}
            else:
                return {"status": "success"}
                
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error: {str(e)}")
            self.request_error.emit("Failed to connect to the backend server. Please check your network connection.")
            return None
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error: {str(e)}")
            self.request_error.emit(f"HTTP error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Request failed: {str(e)}")
            self.request_error.emit(f"Request failed: {str(e)}")
            return None

    # Async wrapper for requests to avoid blocking the UI thread
    class RequestWorker(QThread):
        finished = pyqtSignal(dict)
        error = pyqtSignal(str)
        
        def __init__(self, method_func, *args, **kwargs):
            super().__init__()
            self.method_func = method_func
            self.args = args
            self.kwargs = kwargs
            
        def run(self):
            try:
                result = self.method_func(*self.args, **self.kwargs)
                if result is not None:
                    self.finished.emit(result)
            except Exception as e:
                self.error.emit(str(e))
    
    def _async_request(self, method_func, *args, **kwargs):
        """Execute a request in a background thread"""
        worker = self.RequestWorker(method_func, *args, **kwargs)
        worker.finished.connect(self.request_finished)
        worker.error.connect(self.request_error)
        worker.start()
        return worker
    
    # Project API methods
    def get_projects(self):
        """Get all projects"""
        return self._make_request('get', 'projects/')
        
    def get_projects_async(self):
        """Get all projects asynchronously"""
        return self._async_request(self.get_projects)
        
    def get_project(self, project_id):
        """Get details for a specific project"""
        return self._make_request('get', f'projects/{project_id}/')
        
    def create_project(self, project_data):
        """Create a new project"""
        return self._make_request('post', 'projects/', data=project_data)
        
    def update_project(self, project_id, project_data):
        """Update an existing project"""
        return self._make_request('put', f'projects/{project_id}/', data=project_data)
        
    def delete_project(self, project_id):
        """Delete a project"""
        return self._make_request('delete', f'projects/{project_id}/')
    
    # Document API methods
    def get_documents(self, project_id=None):
        """Get all documents, optionally filtered by project"""
        params = {}
        if project_id:
            params['project_id'] = project_id
        return self._make_request('get', 'documents/', params=params)
        
    def get_documents_async(self, project_id=None):
        """Get all documents asynchronously"""
        params = {}
        if project_id:
            params['project_id'] = project_id
        return self._async_request(self._make_request, 'get', 'documents/', params=params)
        
    def get_document(self, document_id):
        """Get details for a specific document"""
        return self._make_request('get', f'documents/{document_id}/')
        
    def add_document(self, document_data, file=None):
        """Add a new document with optional file attachment"""
        if file:
            files = {'file': file}
            return self._make_request('post', 'documents/', data=document_data, files=files)
        else:
            return self._make_request('post', 'documents/', data=document_data)
            
    def add_document_async(self, document_data, file=None):
        """Add a new document asynchronously"""
        return self._async_request(self.add_document, document_data, file)
        
    def update_document(self, document_id, document_data):
        """Update an existing document"""
        return self._make_request('put', f'documents/{document_id}/', data=document_data)
        
    def delete_document(self, document_id):
        """Delete a document"""
        return self._make_request('delete', f'documents/{document_id}/')
    
    # User API methods
    def login(self, username, password):
        """Login and get authentication token"""
        return self._make_request('post', 'auth/login/', data={'username': username, 'password': password})
        
    def logout(self):
        """Logout and invalidate token"""
        result = self._make_request('post', 'auth/logout/')
        self.set_token(None)
        return result
    
    # Additional methods for other API endpoints as needed
    def get_workflows(self):
        """Get all workflows"""
        return self._make_request('get', 'workflows/')
        
    def get_analytics(self):
        """Get analytics data"""
        return self._make_request('get', 'analytics/')
        
    def get_storage_info(self):
        """Get storage information"""
        return self._make_request('get', 'storage/info/')

# Create a global instance for use throughout the application
api_client = APIClient()