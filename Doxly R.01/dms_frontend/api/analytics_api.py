import requests
from config import BACKEND_API_URL

class AuthAPI:
    """Handles authentication-related API requests."""

    def __init__(self):
        self.base_url = f"{BACKEND_API_URL}/auth/"

    def login(self, username, password):
        """Send login request and return user data."""
        url = f"{self.base_url}login/"
        response = requests.post(url, json={"username": username, "password": password})
        return response.json() if response.status_code == 200 else None

    def logout(self, token):
        """Send logout request to invalidate session."""
        url = f"{self.base_url}logout/"
        headers = {"Authorization": f"Token {token}"}
        response = requests.post(url, headers=headers)
        return response.status_code == 204

    def get_user_profile(self, token):
        """Fetch user profile details."""
        url = f"{self.base_url}profile/"
        headers = {"Authorization": f"Token {token}"}
        response = requests.get(url, headers=headers)
        return response.json() if response.status_code == 200 else None
