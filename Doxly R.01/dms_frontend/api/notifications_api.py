import logging
import requests
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class NotificationAPI:
    """Handles notification-related API communications"""
    
    def __init__(self, base_url: str = "http://localhost:8000/api/notifications"):
        self.base_url = base_url
        
    def _get_headers(self, token: str) -> Dict[str, str]:
        return {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
    
    def get_notifications(self, token: str) -> List[Dict[str, Any]]:
        """Get all notifications"""
        try:
            response = requests.get(
                f"{self.base_url}/",
                headers=self._get_headers(token),
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get notifications: {str(e)}")
            return []
    
    def mark_as_read(self, token: str, notification_id: str) -> bool:
        """Mark notification as read"""
        try:
            response = requests.post(
                f"{self.base_url}/mark_as_read/",
                headers=self._get_headers(token),
                json={"id": notification_id},
                timeout=10
            )
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to mark notification as read: {str(e)}")
            return False