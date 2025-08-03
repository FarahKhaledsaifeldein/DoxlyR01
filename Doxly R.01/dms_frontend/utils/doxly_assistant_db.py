import datetime
import re
import os
import random
import pyttsx3

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QScrollArea, QPushButton, QLineEdit, QLabel, QDialog, QFormLayout, QHBoxLayout, QVBoxLayout, QListWidget, QFrame
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QTimer

# Import database integration
from .db_integration import DoxlyDatabaseIntegration

class DoxlyAssistant:
    """Assistant for processing user queries with database integration"""
    
    def __init__(self):
        self.token = None
        self.username = None
        self.reminders = []
        self.document_context = {}
        self.language = "English"
        self.voice_enabled = True
        self.voice_rate = 150
        self.voice_volume = 1.0
        self.voice_language = "English"
        self.voice_gender = "female"  # Default voice gender preference
        
        # Database integration (will be initialized when username is set)
        self.db = None
        
        # Load responses for different languages
        self.responses = self._load_responses()
        
        # Initialize NLP capabilities
        self._init_nlp()
        
        # Initialize text-to-speech engine - do this AFTER voice settings are defined
        self._init_tts()
    
    def set_username(self, username):
        """Set the username and initialize database integration"""
        self.username = username
        
        # Initialize database integration
        try:
            self.db = DoxlyDatabaseIntegration(username)
            
            # Load settings from database
            self._load_settings_from_db()
            
            # Sync any existing reminders to database
            self._sync_reminders_to_db()
            
            return True
        except Exception as e:
            print(f"Error initializing database integration: {str(e)}")
            self.db = None
            return False
    
    def _load_settings_from_db(self):
        """Load assistant settings from database"""
        if self.db is None:
            return
            
        try:
            settings = self.db.get_assistant_settings()
            
            # Apply settings
            if 'language' in settings:
                self.language = settings['language']
                
            if 'voice_enabled' in settings:
                self.voice_enabled = settings['voice_enabled']
                
            if 'voice_rate' in settings:
                self.voice_rate = settings['voice_rate']
                
            if 'voice_volume' in settings:
                self.voice_volume = settings['voice_volume']
                
            if 'voice_language' in settings:
                self.voice_language = settings['voice_language']
                
            if 'voice_gender' in settings:
                self.voice_gender = settings['voice_gender']
                
            # Update TTS engine with new settings if it exists
            if self.tts_engine:
                self.tts_engine.setProperty('rate', self.voice_rate)
                self.tts_engine.setProperty('volume', self.voice_volume)
                self._set_voice_by_language_and_gender(self.voice_language, self.voice_gender)
        except Exception as e:
            print(f"Error loading settings from database: {str(e)}")
    
    def _sync_reminders_to_db(self):
        """Sync in-memory reminders to database"""
        if self.db is None or not self.reminders:
            return
            
        try:
            for reminder in self.reminders:
                if not reminder.get('synced_to_db', False):
                    self.db.add_reminder(reminder['task'], reminder['time'])
                    reminder['synced_to_db'] = True
        except Exception as e:
            print(f"Error syncing reminders to database: {str(e)}")
    
    def _load_responses(self):
        """Load response templates for different languages"""
        # Default English responses
        responses = {
            "English": {
                "greeting": [
                    "Hello! How can I help you today?",
                    "Hi there! I'm Doxly, your assistant. What can I do for you?",
                    "Good day! How may I assist you?"
                ],
                "farewell": [
                    "Goodbye! Have a great day!",
                    "See you later!",
                    "Until next time!"
                ],
                "confirmation": [
                    "I've completed that for you.",
                    "Done!",
                    "Task completed successfully."
                ],
                "confusion": [
                    "I'm not sure I understand. Could you rephrase that?",
                    "I didn't quite catch that. Can you say it differently?",
                    "I'm still learning. Could you be more specific?"
                ],
                "reminder_set": [
                    "I've set a reminder for {time}: {task}",
                    "I'll remind you about {task} at {time}",
                    "Reminder set for {time} to {task}"
                ],
                "document_info": [
                    "Here's what I found about that document: {info}",
                    "I've found this information: {info}",
                    "Here are the document details: {info}"
                ]
            },
            "Arabic": {
                "greeting": [
                    "مرحبًا! كيف يمكنني مساعدتك اليوم؟",
                    "أهلاً! أنا دوكسلي، مساعدك. ماذا يمكنني أن أفعل لك؟",
                    "يوم سعيد! كيف يمكنني مساعدتك؟"
                ],
                "farewell": [
                    "وداعًا! أتمنى لك يومًا رائعًا!",
                    "إلى اللقاء!",
                    "حتى المرة القادمة!"
                ],
                "confirmation": [
                    "لقد أكملت ذلك من أجلك.",
                    "تم!",
                    "تم إكمال المهمة بنجاح."
                ],
                "confusion": [
                    "لست متأكدًا من فهمي. هل يمكنك إعادة صياغة ذلك؟",
                    "لم أفهم ذلك تمامًا. هل يمكنك قوله بطريقة مختلفة؟",
                    "ما زلت أتعلم. هل يمكنك أن تكون أكثر تحديدًا؟"
                ],
                "reminder_set": [
                    "لقد قمت بتعيين تذكير لـ {time}: {task}",
                    "سأذكرك بـ {task} في {time}",
                    "تم تعيين تذكير لـ {time} لـ {task}"
                ],
                "document_info": [
                    "إليك ما وجدته حول هذا المستند: {info}",
                    "لقد وجدت هذه المعلومات: {info}",
                    "إليك تفاصيل المستند: {info}"
                ]
            },
            # Spanish language support removed as per requirements
            # Add more languages as needed
        }
        return responses
    
    def _init_nlp(self):
        """Initialize NLP capabilities"""
        # Define intent patterns for different actions
        self.intent_patterns = {
            "greeting": [
                r"\b(hello|hi|hey|greetings)\b",
                r"\bgood\s(morning|afternoon|evening)\b"
            ],
            "farewell": [
                r"\b(goodbye|bye|see\syou|farewell)\b"
            ],
            "reminder": [
                r"remind\s+me\s+to\s+(.+?)\s+at\s+(.+)",
                r"set\s+(?:a\s+)?reminder\s+(?:for\s+)?(.+?)\s+(?:at|on)\s+(.+)"
            ],
            "open_settings": [
                r"\b(open|show|display)\s+(settings|preferences|options)\b"
            ],
            "document_search": [
                r"\b(find|search|locate)\s+(?:for\s+)?(?:a\s+)?(?:document|file|doc)\s+(?:about|on|named|called)?\s+(.+)\b"
            ],
            "email": [
                r"\b(send|compose|write)\s+(?:an\s+)?email\s+to\s+(.+)\b"
            ],
            "weather": [
                r"\b(what's|what\sis|how's|how\sis)\s+the\s+weather\s+(?:like\s+)?(?:today|now|in\s+(.+))?\b"
            ],
            "schedule": [
                r"\b(what|show|tell\s+me)\s+(?:do\s+I\s+have|is|about)\s+(?:my\s+)?(schedule|calendar|appointments|events)\s+(?:for\s+)?(today|tomorrow|this\s+week|next\s+week|.+)?\b"
            ]
        }
    
    def process_query(self, query):
        """Process a user query and return an appropriate response"""
        query = query.lower().strip()
        
        # Check for intents
        intent, entities = self._detect_intent(query)
        
        # Generate response based on intent
        if intent == "greeting":
            response = random.choice(self.responses[self.language]["greeting"])
        
        elif intent == "farewell":
            response = random.choice(self.responses[self.language]["farewell"])
        
        elif intent == "reminder":
            task, time = entities
            self._set_reminder(task, time)
            response = self.responses[self.language]["reminder_set"][0].format(time=time, task=task)
        
        elif intent == "open_settings":
            # This will be handled by the UI component
            response = "Opening settings for you."
        
        elif intent == "document_search":
            document_name = entities[0] if entities else ""
            response = f"Searching for documents related to {document_name}..."
        
        elif intent == "email":
            recipient = entities[0] if entities else ""
            response = f"Opening email composer to send a message to {recipient}..."
        
        elif intent == "weather":
            location = entities[0] if entities else "today"
            response = f"I would check the weather for {location}, but I don't have access to weather data yet."
        
        elif intent == "schedule":
            time_period = entities[0] if entities else "today"
            response = f"Here's your schedule for {time_period}... (This would show your actual schedule)"
        
        else:
            response = random.choice(self.responses[self.language]["confusion"])
        
        # Speak the response if voice is enabled
        if self.voice_enabled:
            self.speak(response)
            
        return response
    
    def _detect_intent(self, query):
        """Detect the intent and extract entities from a query"""
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, query, re.IGNORECASE)
                if match:
                    # Extract entities (captured groups)
                    entities = match.groups()[1:] if len(match.groups()) > 1 else match.groups()
                    return intent, entities
        
        return "unknown", None
    
    def _set_reminder(self, task, time_str):
        """Set a reminder for a specific task at a specific time"""
        # Parse time string to datetime object (simplified)
        try:
            # This is a simplified version - in a real app, you'd use a more robust time parser
            if time_str.lower() == "tomorrow":
                reminder_time = datetime.datetime.now() + datetime.timedelta(days=1)
            elif ":" in time_str:
                # Assume format like "8:00 PM"
                hour, minute = time_str.split(":")[0], time_str.split(":")[1].split(" ")[0]
                am_pm = time_str.split(" ")[1] if len(time_str.split(" ")) > 1 else ""
                
                hour = int(hour)
                minute = int(minute)
                
                if am_pm.lower() == "pm" and hour < 12:
                    hour += 12
                
                now = datetime.datetime.now()
                reminder_time = now.replace(hour=hour, minute=minute)
                
                # If the time is in the past, set it for tomorrow
                if reminder_time < now:
                    reminder_time += datetime.timedelta(days=1)
            else:
                # Default to 1 hour from now
                reminder_time = datetime.datetime.now() + datetime.timedelta(hours=1)
            
            # Add to in-memory list
            self.reminders.append({
                "task": task,
                "time": reminder_time,
                "completed": False
            })
            
            # Save to database if available
            if self.db is not None:
                self.db.add_reminder(task, reminder_time)
            
            return True
        except Exception as e:
            print(f"Error setting reminder: {str(e)}")
            return False
    
    def get_active_reminders(self):
        """Get all active (non-completed) reminders"""
        # If database is available, get reminders from there
        if self.db is not None:
            return self.db.get_active_reminders()
        
        # Otherwise use in-memory storage
        now = datetime.datetime.now()
        active_reminders = []
        
        for reminder in self.reminders:
            if not reminder["completed"] and reminder["time"] > now:
                active_reminders.append(reminder)
        
        return active_reminders
    
    def check_due_reminders(self):
        """Check for reminders that are due"""
        # If database is available, get due reminders from there
        if self.db is not None:
            return self.db.get_due_reminders()
        
        # Otherwise use in-memory storage
        now = datetime.datetime.now()
        due_reminders = []
        
        for reminder in self.reminders:
            if not reminder["completed"] and reminder["time"] <= now:
                reminder["completed"] = True
                due_reminders.append(reminder)
        
        return due_reminders
    
    def set_language(self, language):
        """Set the assistant's language"""
        if language in self.responses:
            self.language = language
            
            # Update database if available
            if self.db is not None:
                self.db.update_assistant_settings({'language': language})
                
            return True
        return False
    
    def learn_from_documents(self, document_name, document_data):
        """Learn from document content to improve contextual awareness"""
        # In a real implementation, this would analyze document content
        # and extract key information to improve assistant responses
        self.document_context.update(document_data)
        
        # Store in database if available
        if self.db is not None:
            self.db.add_document_context(document_name, document_data)
    
    def _init_tts(self):
        """Initialize text-to-speech engine with robust error handling"""
        self.tts_engine = None
        self.available_voices = {"English": {"male": [], "female": []}, "Arabic": {"male": [], "female": []}}
        self.arabic_voice_fixed = False  # Flag to track if Arabic voice has been fixed
        
        # Try to load settings from database if available
        self._load_settings_from_db()
        
        # First attempt - standard initialization
        try:
            print("Initializing text-to-speech engine...")
            self.tts_engine = pyttsx3.init()
            
            # Get available voices
            voices = self.tts_engine.getProperty('voices')
            if not voices or len(voices) == 0:
                print("Warning: No voices found in TTS engine")
                # Continue anyway, we'll handle this later
            
            # Categorize available voices by language and gender
            self.available_voices = self._categorize_voices(voices)
            
            # Set default voice based on language and gender preference
            voice_set = self._set_voice_by_language_and_gender(self.language, self.voice_gender)
            if not voice_set and voices and len(voices) > 0:
                # Fallback to first available voice if categorization failed
                print("Using default voice as fallback")
                self.tts_engine.setProperty('voice', voices[0].id)
            
            # Set default rate and volume
            self.tts_engine.setProperty('rate', self.voice_rate)
            self.tts_engine.setProperty('volume', self.voice_volume)
            
            # Test the engine with a silent message to ensure it's working
            self._test_tts_engine()
            
        except Exception as e:
            print(f"Primary TTS initialization error: {str(e)}")
            self._try_fallback_tts_init()
    
    def set_voice_enabled(self, enabled):
        """Enable or disable voice output"""
        self.voice_enabled = enabled
        
        # Update database if available
        if self.db is not None:
            self.db.update_assistant_settings({'voice_enabled': enabled})
    
    def set_voice_language(self, language):
        """Set voice language"""
        self.voice_language = language
        
        # Update voice if TTS engine is available
        if self.tts_engine:
            self._set_voice_by_language_and_gender(language, self.voice_gender)
        
        # Update database if available
        if self.db is not None:
            self.db.update_assistant_settings({'voice_language': language})
    
    def set_voice_gender(self, gender):
        """Set voice gender preference"""
        self.voice_gender = gender
        
        # Update voice if TTS engine is available
        if self.tts_engine:
            self._set_voice_by_language_and_gender(self.voice_language, gender)
        
        # Update database if available
        if self.db is not None:
            self.db.update_assistant_settings({'voice_gender': gender})
    
    def set_voice_rate(self, rate):
        """Set voice speaking rate"""
        self.voice_rate = rate
        
        # Update TTS engine if available
        if self.tts_engine:
            self.tts_engine.setProperty('rate', rate)
        
        # Update database if available
        if self.db is not None:
            self.db.update_assistant_settings({'voice_rate': rate})
    
    def set_voice_volume(self, volume):
        """Set voice volume"""
        self.voice_volume = volume
        
        # Update TTS engine if available
        if self.tts_engine:
            self.tts_engine.setProperty('volume', volume)
        
        # Update database if available
        if self.db is not None:
            self.db.update_assistant_settings({'voice_volume': volume})

    # The rest of the DoxlyAssistant class methods would remain the same
    # This includes methods like _test_tts_engine, _try_fallback_tts_init, _categorize_voices, etc.
    # For brevity, they are not included here