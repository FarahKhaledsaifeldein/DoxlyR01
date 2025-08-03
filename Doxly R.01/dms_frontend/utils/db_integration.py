import os
import datetime
from .database import get_database

class DoxlyDatabaseIntegration:
    """Integration layer between Doxly Assistant and the local SQLite database"""
    
    def __init__(self, username=None):
        """Initialize the database integration"""
        self.db = get_database()
        self.username = username
        self.user_id = None
        
        # If username is provided, ensure user exists in database
        if username:
            self._ensure_user_exists()
    
    def _ensure_user_exists(self):
        """Ensure the current user exists in the database"""
        user = self.db.get_user(self.username)
        if not user:
            # Create user if doesn't exist
            self.user_id = self.db.add_user(self.username)
        else:
            self.user_id = user['id']
    
    def set_username(self, username):
        """Set or update the username"""
        self.username = username
        self._ensure_user_exists()
    
    # Reminder methods
    def add_reminder(self, task, reminder_time):
        """Add a reminder to the database"""
        if not self.user_id:
            return False
            
        return self.db.add_reminder(self.user_id, task, reminder_time)
    
    def get_active_reminders(self):
        """Get all active reminders for the current user"""
        if not self.user_id:
            return []
            
        reminders = self.db.get_active_reminders(self.user_id)
        
        # Convert database format to assistant format
        formatted_reminders = []
        for reminder in reminders:
            # Parse ISO format datetime string
            reminder_time = datetime.datetime.fromisoformat(reminder['reminder_time'])
            
            formatted_reminders.append({
                'task': reminder['task'],
                'time': reminder_time,
                'completed': bool(reminder['completed'])
            })
            
        return formatted_reminders
    
    def get_due_reminders(self):
        """Get all due reminders for the current user"""
        if not self.user_id:
            return []
            
        reminders = self.db.get_due_reminders(self.user_id)
        
        # Convert database format to assistant format
        formatted_reminders = []
        for reminder in reminders:
            # Parse ISO format datetime string
            reminder_time = datetime.datetime.fromisoformat(reminder['reminder_time'])
            
            formatted_reminders.append({
                'task': reminder['task'],
                'time': reminder_time,
                'completed': True  # Due reminders are automatically marked as completed
            })
            
        return formatted_reminders
    
    # Document context methods
    def add_document_context(self, document_name, context_data):
        """Store document context information"""
        if not self.user_id:
            return False
            
        # Search for document by name
        documents = self.db.search_documents(document_name)
        
        # If document exists, update its metadata
        if documents:
            document = documents[0]
            document_id = document['id']
            
            # Get existing metadata and update it
            existing_metadata = document.get('metadata', '{}')
            if isinstance(existing_metadata, str):
                import json
                try:
                    metadata = json.loads(existing_metadata)
                except json.JSONDecodeError:
                    metadata = {}
            else:
                metadata = existing_metadata
                
            # Update with new context data
            metadata.update(context_data)
            
            # TODO: Implement update_document_metadata method in database.py
            # For now, we'll just store this in memory
            return True
        
        return False
    
    def get_document_context(self, document_name):
        """Retrieve document context information"""
        if not self.user_id:
            return {}
            
        # Search for document by name
        documents = self.db.search_documents(document_name)
        
        if documents:
            document = documents[0]
            metadata = document.get('metadata', '{}')
            
            # Parse metadata JSON
            if isinstance(metadata, str):
                import json
                try:
                    return json.loads(metadata)
                except json.JSONDecodeError:
                    return {}
            else:
                return metadata
        
        return {}
    
    # Settings methods
    def get_assistant_settings(self):
        """Get assistant-related settings"""
        # Get voice assistant settings
        voice_settings = self.db.get_settings('voice_assistant')
        
        # Convert string values to appropriate types
        settings = {
            'voice_enabled': voice_settings.get('voice_enabled', '1') == '1',
            'voice_rate': int(voice_settings.get('voice_rate', '150')),
            'voice_volume': float(voice_settings.get('voice_volume', '1.0')),
            'voice_language': voice_settings.get('voice_language', 'English'),
            'voice_gender': voice_settings.get('voice_gender', 'female')
        }
        
        # Get application language setting
        app_settings = self.db.get_settings('application')
        settings['language'] = app_settings.get('language', 'English')
        
        return settings
    
    def update_assistant_settings(self, settings):
        """Update assistant-related settings"""
        # Update voice assistant settings
        if 'voice_enabled' in settings:
            self.db.update_setting('voice_enabled', '1' if settings['voice_enabled'] else '0')
        
        if 'voice_rate' in settings:
            self.db.update_setting('voice_rate', str(settings['voice_rate']))
        
        if 'voice_volume' in settings:
            self.db.update_setting('voice_volume', str(settings['voice_volume']))
        
        if 'voice_language' in settings:
            self.db.update_setting('voice_language', settings['voice_language'])
        
        if 'voice_gender' in settings:
            self.db.update_setting('voice_gender', settings['voice_gender'])
        
        # Update application language if provided
        if 'language' in settings:
            self.db.update_setting('language', settings['language'])
        
        return True