import requests
from config import BACKEND_API_URL
from datetime import datetime, timedelta



class AuthAPI:
    def __init__(self):
        self.base_url = f"{BACKEND_API_URL}users/"
        self.token = None          # Stores the JWT access token
        self.refresh_token = None  # Stores the refresh token
        self.expires_at = None     # Token expiration time

    def login(self, username: str, password: str) -> dict:
        """Authenticate and store tokens"""
        try:
            response = requests.post(
                f"{self.base_url}login/",
                json={"username": username, "password": password},
                timeout=300
            )
            data = response.json()

            if response.status_code == 200:
                # Store tokens and calculate expiration
                self.token = data.get('access')
                self.refresh_token = data.get('refresh')
                expires_in = data.get('expires_in', 7200)  # Default: 2 hours
                self.expires_at = datetime.now() + timedelta(seconds=expires_in)
                
                return {
                   "success": True,
                    "token": data.get('access'),
                    "expires_at": (datetime.now() + timedelta(seconds=data.get('expires_in', 7200))).isoformat(),
                     "user_data": data.get('user', {})
                         }
            else:
                return {"error": data.get('detail', 'Login failed')}

        except Exception as e:
            return {"error": str(e)}

    def is_authenticated(self) -> bool:
        """Check if token exists and is valid"""
        return (
            self.token and 
            self.expires_at and 
            datetime.now() < self.expires_at
        )

    def get_auth_header(self) -> dict:
        """Generate headers with current token"""
        if not self.is_authenticated():
            raise Exception("Not authenticated or session expired")
        return {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json"
        }
    def register(self, username, email, password):
        """Send registration request."""
        url = f"{self.base_url}register/"
        try:
            response = requests.post(url, json={
                "username": username,
                "email": email,
                "password": password,
                "password2": password,  # Add confirmation password as required by backend
                "role": "viewer"  # Default role for new users
            })
            if response.status_code == 201:
                return {"message": "Registration successful", "data": response.json()}
            elif response.status_code == 400:
                error_data = response.json()
                if "errors" in error_data:
                    return {"error": str(error_data["errors"])}
                return {"error": error_data.get("message", "Registration failed. Please check your input.")}
            else:
                return {"error": "Registration failed. Please try again later."}
        except requests.exceptions.RequestException as e:
            return {"error": f"Connection error: {str(e)}"}

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
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                return {"error": "Authentication failed. Please log in again."}
            else:
                return {"error": f"Failed to fetch profile. Status code: {response.status_code}"}
        except requests.exceptions.RequestException as e:
            return {"error": f"Connection error: {str(e)}"}
    
    def update_profile(self, token, profile_data):
        """Update user profile and preferences."""
        url = f"{self.base_url}profile/"
        headers = {"Authorization": f"Token {token}"}
        try:
            response = requests.put(url, json=profile_data, headers=headers)
            if response.status_code == 200:
                return {"message": "Profile updated successfully", "data": response.json()}
            elif response.status_code == 400:
                error_data = response.json()
                return {"error": error_data.get("message", "Invalid profile data")}
            elif response.status_code == 401:
                return {"error": "Authentication failed. Please log in again."}
            else:
                return {"error": f"Failed to update profile. Status code: {response.status_code}"}
        except requests.exceptions.RequestException as e:
            return {"error": f"Connection error: {str(e)}"}
    
    def change_password(self, token, current_password, new_password):
        """Change user password."""
        url = f"{self.base_url}change-password/"
        headers = {"Authorization": f"Token {token}"}
        data = {
            "current_password": current_password,
            "new_password": new_password
        }
        
        try:
            response = requests.post(url, json=data, headers=headers)
            if response.status_code == 200:
                return {"message": "Password changed successfully"}
            elif response.status_code == 400:
                error_data = response.json()
                return {"error": error_data.get("message", "Invalid password data")}
            elif response.status_code == 401:
                return {"error": "Current password is incorrect"}
            else:
                return {"error": f"Failed to change password. Status code: {response.status_code}"}
        except requests.exceptions.RequestException as e:
            return {"error": f"Connection error: {str(e)}"}