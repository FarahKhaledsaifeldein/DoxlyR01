import requests
from config import BACKEND_API_URL

class StorageAPI:
    """Handles cloud and local storage syncing."""

    def __init__(self):
        self.base_url = f"{BACKEND_API_URL}storage/"

    def sync_with_cloud(self, token, provider):
        """Sync local storage with a cloud provider (Google Drive, AWS, etc.)."""
        headers = {"Authorization": f"Token {token}"}
        data = {"provider": provider}
        response = requests.post(f"{self.base_url}sync/", json=data, headers=headers)
        return response.json() if response.status_code == 200 else None
