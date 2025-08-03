import requests
from config import BACKEND_API_URL

class BaseAPI:
    def __init__(self):
        self.base_url = BACKEND_API_URL
        self.token = None

    def set_token(self, token):
        """Set the authentication token."""
        if token is None or not str(token).strip():
            self.token = None
            return
        try:
            cleaned_token = str(token).strip()
            if cleaned_token.startswith('Token '):
                cleaned_token = cleaned_token[6:]
            self.token = cleaned_token
        except Exception:
            self.token = None

    def get_headers(self):
        """Get headers with authentication token."""
        headers = {
            'Content-Type': 'application/json'
        }
        if self.token:
            # Use Bearer format for JWT tokens
            headers['Authorization'] = f'Bearer {self.token}'
        return headers

    def handle_response(self, response):
        """Handle API response and errors."""
        try:
            if response.status_code == 401:
                return {"error": "Authentication failed: Please log in again"}
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            if response.status_code == 401:
                return {"error": "Authentication failed: Please log in again"}
            return {"error": f"API Error: {str(e)}"}