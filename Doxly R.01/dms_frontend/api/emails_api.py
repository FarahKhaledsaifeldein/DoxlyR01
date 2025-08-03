import requests
from config import BACKEND_API_URL
from typing import List, Dict, Any, Optional, Tuple, IO
import os
import logging
logger = logging.getLogger(__name__)
from django.core.exceptions import ValidationError
class EmailAPI:

    """Handles all email-related API communications with multipart form data support"""
    
    def __init__(self, base_url: str = "http://localhost:8000/api/notifications"):
        self.base_url = base_url
        
    def _get_headers(self, token: str, multipart: bool = False) -> Dict[str, str]:
        headers = {
            'Authorization': f'Bearer {token}'
        }
        if not multipart:
            headers['Content-Type'] = 'application/json'
        return headers
    
    def get_emails(self, token: str, folder: str = "inbox") -> List[Dict[str, Any]]:
        """Retrieve emails from specified folder"""
        try:
            response = requests.get(
                f"{self.base_url}/emails/?status=sent",
                headers=self._get_headers(token),
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get emails: {str(e)}")
            return []
    
    def send_email(
        self, 
        token: str, 
        email_data: Dict[str, Any], 
        attachments: List[Tuple[str, str]] = None
    ) -> bool:
        """
        Send an email with optional attachments using multipart form data
        
        Args:
            token: Authentication token
            email_data: Dictionary containing email fields (to, subject, body, etc.)
            attachments: List of tuples (filename, filepath)
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Prepare files for multipart upload
            files = []
            if attachments:
                for filename, filepath in attachments:
                    if os.path.exists(filepath):
                        files.append(
                            ('attachments', (filename, open(filepath, 'rb'))
                        )
                        )
            
            # Prepare form data
            form_data = {
                'recipient_email': email_data.get('to', ''),
                'subject': email_data.get('subject', ''),
                'body': email_data.get('body', ''),
                'cc': email_data.get('cc', ''),
                'bcc': email_data.get('bcc', '')
            }
            
            response = requests.post(
                f"{self.base_url}/email/send/",
                headers=self._get_headers(token, multipart=True),
                
                data=form_data,
                files=files,
                timeout=30
            )
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send email: {str(e)}")
            return False
        finally:
            # Close all file handles
            for file_tuple in files:
                file_tuple[1][1].close()
    
    def get_drafts(self, token: str) -> List[Dict[str, Any]]:
        """Retrieve draft emails"""
        try:
            response = requests.get(
                f"{self.base_url}/emails/drafts/",
                headers=self._get_headers(token),
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get drafts: {str(e)}")
            return []
    
    def save_draft(
        self, 
        token: str, 
        draft_data: Dict[str, Any], 
        attachments: List[Tuple[str, str]] = None
    ) -> bool:
        """
        Save a draft email with optional attachments using multipart form data
        
        Args:
            token: Authentication token
            draft_data: Dictionary containing email fields (to, subject, body, etc.)
            attachments: List of tuples (filename, filepath)
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Prepare files for multipart upload
            files = []
            if attachments:
                for filename, filepath in attachments:
                    if os.path.exists(filepath):
                        files.append(
                            ('attachments', (filename, open(filepath, 'rb'))
                        )
                        )
            
            # Prepare form data
            form_data = {
                'recipient_email': draft_data.get('to', ''),
                'subject': draft_data.get('subject', ''),
                'body': draft_data.get('body', ''),
                'cc': draft_data.get('cc', ''),
                'bcc': draft_data.get('bcc', '')
            }
            
            response = requests.post(
                f"{self.base_url}/emails/draft/save/",
                headers=self._get_headers(token, multipart=True),
                data=form_data,
                files=files,
                timeout=30
            )
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to save draft: {str(e)}")
            return False
        finally:
            # Close all file handles
            for file_tuple in files:
                file_tuple[1][1].close()
    '''"""    """Handles email notifications and alerts."""

    def __init__(self):
        self.base_url = f"{BACKEND_API_URL}notifications/"

    def get_notifications(self, token):
        """Fetch all notifications for the user."""
        headers = {"Authorization": f"Token {token}"}
        response = requests.get(self.base_url, headers=headers)
        return response.json() if response.status_code == 200 else None

    def mark_as_read(self, token, notification_id):
        """Mark a notification as read."""
        headers = {"Authorization": f"Token {token}"}
        url = f"{self.base_url}{notification_id}/read/"
        response = requests.post(url, headers=headers)
        return response.status_code == 200

import os
import logging
import requests
from typing import List, Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)

"""'''