import datetime
import re
import os
import random
import pyttsx3
import threading

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QScrollArea, QPushButton, QLineEdit, QLabel, QDialog, QFormLayout, QHBoxLayout, QVBoxLayout, QListWidget, QFrame
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QTimer
from .voice_commands import VoiceCommandHandler


class DoxlyAssistant:
    """Assistant for processing user queries"""
    
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
                
            self.reminders.append({
                "task": task,
                "time": reminder_time,
                "completed": False
            })
            
            return True
        except Exception as e:
            print(f"Error setting reminder: {str(e)}")
            return False
    
    def get_active_reminders(self):
        """Get all active (non-completed) reminders"""
        now = datetime.datetime.now()
        active_reminders = []
        
        for reminder in self.reminders:
            if not reminder["completed"] and reminder["time"] > now:
                active_reminders.append(reminder)
        
        return active_reminders
    
    def check_due_reminders(self):
        """Check for reminders that are due"""
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
            return True
        return False
    
    def learn_from_documents(self, document_data):
        """Learn from document content to improve contextual awareness"""
        # In a real implementation, this would analyze document content
        # and extract key information to improve assistant responses
        self.document_context.update(document_data)
        
    def _init_tts(self):
        """Initialize text-to-speech engine with robust error handling"""
        self.tts_engine = None
        self.available_voices = {"English": {"male": [], "female": []}, "Arabic": {"male": [], "female": []}}
        self.arabic_voice_fixed = False  # Flag to track if Arabic voice has been fixed
        self.selected_voice = None  # Track the currently selected voice
        
        # First attempt - standard initialization
        try:
            print("Initializing text-to-speech engine...")
            # Try to initialize with specific driver first
            try:
                self.tts_engine = pyttsx3.init(driverName='sapi5')  # Windows default
            except:
                # If that fails, try without specifying driver
                self.tts_engine = pyttsx3.init()
            
            # Get available voices
            voices = self.tts_engine.getProperty('voices')
            if not voices or len(voices) == 0:
                print("Warning: No voices found in TTS engine")
                # Continue anyway, we'll handle this later
            else:
                print(f"Found {len(voices)} voices in TTS engine")
            
            # Categorize available voices by language and gender
            self.available_voices = self._categorize_voices(voices)
            
            # Set default voice based on language and gender preference
            voice_set = self._set_voice_by_language_and_gender(self.language, self.voice_gender)
            if not voice_set and voices and len(voices) > 0:
                # Fallback to first available voice if categorization failed
                print("Using default voice as fallback")
                self.tts_engine.setProperty('voice', voices[0].id)
                self.selected_voice = {'id': voices[0].id, 'name': voices[0].name}
            
            # Set default rate and volume
            self.tts_engine.setProperty('rate', self.voice_rate)
            self.tts_engine.setProperty('volume', self.voice_volume)
            
            # Test the engine with a silent message to ensure it's working
            self._test_tts_engine()
            
        except Exception as e:
            print(f"Primary TTS initialization error: {str(e)}")
            self._try_fallback_tts_init()
    
    def _test_tts_engine(self):
        """Test if the TTS engine is working properly"""
        if not self.tts_engine:
            print("Cannot test TTS engine: Engine not initialized")
            return False
            
        try:
            # Save current volume to restore it later
            current_volume = self.tts_engine.getProperty('volume')
            
            # Set volume to 0 for silent test
            self.tts_engine.setProperty('volume', 0)
            self.tts_engine.say("Test")
            
            # Use runAndWait with timeout handling
            try:
                import threading
                import time
                
                # Create a flag to track completion
                completed = [False]
                
                # Define a function to run the TTS engine
                def run_tts():
                    try:
                        self.tts_engine.runAndWait()
                        completed[0] = True
                    except Exception as inner_e:
                        print(f"Inner TTS test error: {str(inner_e)}")
                
                # Start the TTS engine in a separate thread
                tts_thread = threading.Thread(target=run_tts)
                tts_thread.daemon = True
                tts_thread.start()
                
                # Wait for the thread to complete or timeout
                timeout = 3  # 3 seconds timeout
                start_time = time.time()
                while not completed[0] and time.time() - start_time < timeout:
                    time.sleep(0.1)
                
                if not completed[0]:
                    print("TTS test timed out, but continuing anyway")
            except Exception as thread_e:
                print(f"Threading error in TTS test: {str(thread_e)}")
            
            # Restore original volume
            self.tts_engine.setProperty('volume', current_volume)
            print("Text-to-speech engine tested successfully")
            return True
        except Exception as e:
            print(f"TTS engine test failed: {str(e)}")
            return False
    
    def _try_fallback_tts_init(self):
        """Try alternative initialization methods for TTS"""
        try:
            # Try different driver options in sequence
            drivers = ['sapi5', 'nsss', 'espeak', None]  # Windows, macOS, Linux, and default
            
            for driver in drivers:
                try:
                    print(f"Attempting fallback TTS initialization with driver: {driver}...")
                    self.tts_engine = pyttsx3.init(driverName=driver)
                    
                    # Set basic properties
                    self.tts_engine.setProperty('rate', self.voice_rate)
                    self.tts_engine.setProperty('volume', self.voice_volume)
                    
                    # Get available voices
                    voices = self.tts_engine.getProperty('voices')
                    if voices and len(voices) > 0:
                        self.tts_engine.setProperty('voice', voices[0].id)
                        self.selected_voice = {'id': voices[0].id, 'name': voices[0].name}
                        self.available_voices = self._categorize_voices(voices)
                        print(f"Fallback TTS initialization successful with driver: {driver}")
                        return True
                    else:
                        print(f"No voices available with driver: {driver}, trying next option")
                        continue
                except Exception as driver_e:
                    print(f"Error with driver {driver}: {str(driver_e)}")
                    continue
            
            # If we get here, all driver options failed
            print("All TTS initialization attempts failed")
            self.tts_engine = None
            self.voice_enabled = False
            return False
                
        except Exception as e:
            print(f"Fallback TTS initialization failed: {str(e)}")
            self.tts_engine = None
            self.voice_enabled = False
            return False
            
    def _categorize_voices(self, voices):
        """Categorize available voices by language and gender"""
        categorized_voices = {
            "English": {"male": [], "female": []},
            "Arabic": {"male": [], "female": []},
            # Add more languages as needed
        }
        
        # Default fallback voices (in case we can't categorize properly)
        default_voices = []
        
        for voice in voices:
            voice_info = {
                'id': voice.id,
                'name': voice.name,
                'languages': getattr(voice, 'languages', []),
                'gender': getattr(voice, 'gender', None)
            }
            
            default_voices.append(voice_info)
            
            # Try to categorize by name and language attributes
            voice_name = voice.name.lower()
            
            # Check for English voices
            if any(lang_code.startswith('en') for lang_code in voice_info['languages']) or 'english' in voice_name:
                if voice_info['gender'] == 'male' or any(male_indicator in voice_name for male_indicator in ['david', 'james', 'mark', 'male']):
                    categorized_voices["English"]["male"].append(voice_info)
                else:
                    categorized_voices["English"]["female"].append(voice_info)
            
            # Check for Arabic voices - improved detection for Arabic voices
            elif any(lang_code.startswith('ar') for lang_code in voice_info['languages']) or \
                 'arabic' in voice_name or \
                 'arab' in voice_name or \
                 'hani' in voice_name or \
                 'laila' in voice_name or \
                 'maged' in voice_name or \
                 'tarik' in voice_name:
                if voice_info['gender'] == 'male' or any(male_indicator in voice_name for male_indicator in ['male', 'ahmed', 'mohammad', 'maged', 'tarik']):
                    categorized_voices["Arabic"]["male"].append(voice_info)
                else:
                    categorized_voices["Arabic"]["female"].append(voice_info)
        
        # If we couldn't categorize any voices, use defaults
        for language in categorized_voices:
            for gender in categorized_voices[language]:
                if not categorized_voices[language][gender] and default_voices:
                    # Just assign the first voice as a fallback
                    categorized_voices[language][gender] = [default_voices[0]]
                    if len(default_voices) > 1:
                        # Try to assign a different voice for the other gender
                        categorized_voices[language]["male" if gender == "female" else "female"] = [default_voices[1]]
        
        return categorized_voices
    
    def _set_voice_by_language_and_gender(self, language, gender):
        """Set voice based on language and gender preference"""
        if not self.tts_engine:
            print("TTS engine not initialized")
            return False
        
        try:
            # Default to English if the requested language is not available
            if language not in self.available_voices:
                print(f"Language {language} not available, falling back to English")
                language = "English"
            
            # Default to female if the requested gender is not available
            if gender not in ["male", "female"]:
                gender = "female"
            
            # Get voices for the requested language and gender
            voices = self.available_voices[language][gender]
            
            # If no voices are available for the requested combination, try fallbacks
            if not voices:
                print(f"No {gender} voices found for {language}, trying alternative gender")
                # Try the other gender in the same language
                other_gender = "male" if gender == "female" else "female"
                voices = self.available_voices[language][other_gender]
                
                # If still no voices, try English
                if not voices and language != "English":
                    print(f"No voices found for {language}, trying English")
                    voices = self.available_voices["English"][gender]
                    
                    # If still no voices, try any available voice
                    if not voices:
                        print("No specific voices found, using any available voice")
                        voices = self.available_voices["English"][other_gender]
            
            # Set the voice if we found one
            if voices:
                self.selected_voice = voices[0]
                self.tts_engine.setProperty('voice', voices[0]['id'])
                print(f"Set voice to: {voices[0]['name']}")
                self.voice_language = language
                self.voice_gender = gender
                return True
            else:
                # Last resort: try to get any voice from the engine
                all_voices = self.tts_engine.getProperty('voices')
                if all_voices and len(all_voices) > 0:
                    print("Using first available voice as last resort")
                    self.tts_engine.setProperty('voice', all_voices[0].id)
                    self.selected_voice = {
                        'id': all_voices[0].id,
                        'name': all_voices[0].name
                    }
                    return True
            
            print("Failed to find any suitable voice")
            return False
        except Exception as e:
            print(f"Error setting voice: {str(e)}")
            return False
    
    def speak(self, text):
        """Convert text to speech with robust error handling"""
        if not text or not isinstance(text, str):
            print("Invalid text provided to speak method")
            return False
            
        # Check if TTS engine is initialized, try to initialize if not
        if not self.tts_engine:
            print("TTS engine not initialized, attempting to initialize now...")
            self._init_tts()
            
            # If initialization failed, return early
            if not self.tts_engine:
                print("Failed to initialize TTS engine")
                return False
            
        if not self.voice_enabled:
            print("Voice output is disabled")
            return False
            
        try:
            # Ensure volume and rate are properly set before speaking
            self.tts_engine.setProperty('volume', self.voice_volume)
            self.tts_engine.setProperty('rate', self.voice_rate)
            
            # Fix for Arabic language - ensure it speaks Arabic text properly
            # If the text contains Arabic characters or language is set to Arabic
            is_arabic_text = any(ord(char) > 1500 for char in text)  # Simple check for Arabic Unicode range
            if is_arabic_text or self.language == "Arabic":
                print(f"Using Arabic voice settings: {self.language}, {self.voice_gender}")
                # Try to find and set an Arabic voice
                if self.available_voices["Arabic"]["female"] or self.available_voices["Arabic"]["male"]:
                    arabic_voice = (self.available_voices["Arabic"]["female"][0] if self.available_voices["Arabic"]["female"] 
                                   else self.available_voices["Arabic"]["male"][0])
                    self.tts_engine.setProperty('voice', arabic_voice['id'])
                    print(f"Set Arabic voice: {arabic_voice['name']}")
                    # Save this as the selected voice
                    self.selected_voice = arabic_voice
            # Check if a voice is selected, use default if not
            elif not self.selected_voice:
                voices = self.tts_engine.getProperty('voices')
                if voices and len(voices) > 0:
                    print("No voice selected, using default voice")
                    self.tts_engine.setProperty('voice', voices[0].id)
                    self.selected_voice = {'id': voices[0].id, 'name': voices[0].name}
            
            # Use a separate thread to avoid blocking the UI
            def speak_thread():
                try:
                    # Ensure the engine is ready
                    import time
                    
                    # Say the text
                    self.tts_engine.say(text)
                    
                    # Use a timeout mechanism for runAndWait
                    completed = [False]
                    error = [None]
                    
                    def run_tts():
                        try:
                            self.tts_engine.runAndWait()
                            completed[0] = True
                        except Exception as run_e:
                            error[0] = run_e
                    
                    # Start the TTS in a separate thread
                    tts_thread = threading.Thread(target=run_tts)
                    tts_thread.daemon = True
                    tts_thread.start()
                    
                    # Wait for completion or timeout
                    timeout = 5  # 5 seconds timeout
                    start_time = time.time()
                    while not completed[0] and time.time() - start_time < timeout:
                        time.sleep(0.1)
                    
                    if not completed[0]:
                        print("TTS runAndWait timed out")
                        if error[0]:
                            print(f"TTS error: {str(error[0])}")
                    else:
                        print(f"Successfully spoke: {text[:30]}{'...' if len(text) > 30 else ''}")
                        
                except RuntimeError as re:
                    # Handle specific runtime errors that can occur during speech
                    print(f"Runtime error in speech thread: {str(re)}")
                    # If the error indicates the engine is busy, wait and try again
                    if "in use" in str(re).lower() or "busy" in str(re).lower():
                        try:
                            print("TTS engine busy, retrying after delay...")
                            time.sleep(0.5)  # Short delay
                            self.tts_engine.say(text)
                            self.tts_engine.runAndWait()
                        except Exception as retry_e:
                            print(f"Retry failed: {str(retry_e)}")
                except Exception as inner_e:
                    print(f"Error in speech thread: {str(inner_e)}")
            
            thread = threading.Thread(target=speak_thread)
            thread.daemon = True  # Thread will close when main program exits
            thread.start()
            return True
        except Exception as e:
            print(f"Error setting up speech thread: {str(e)}")
            # Try to reinitialize the engine for next time
            try:
                print("Attempting to reinitialize TTS engine after error...")
                self._try_fallback_tts_init()
            except Exception:
                pass  # Silently ignore if reinitialization fails
            return False
        
    def set_voice_language(self, language):
        """Set the voice language"""
        if language in self.available_voices:
            self.voice_language = language
            result = self._set_voice_by_language_and_gender(language, self.voice_gender)
            print(f"Voice language set to {language}, result: {result}")
            return result
        print(f"Language {language} not available in voice options")
        return False
        
    def set_voice_gender(self, gender):
        """Set the voice gender"""
        if gender in ["male", "female"]:
            self.voice_gender = gender
            result = self._set_voice_by_language_and_gender(self.voice_language, gender)
            print(f"Voice gender set to {gender}, result: {result}")
            return result
        print(f"Gender {gender} not valid, must be 'male' or 'female'")
        return False
    
    def set_voice_enabled(self, enabled):
        """Enable or disable voice output"""
        self.voice_enabled = bool(enabled)
        print(f"Voice output {'enabled' if self.voice_enabled else 'disabled'}")
        return True
    
    def set_voice_rate(self, rate):
        """Set the speech rate (words per minute)"""
        try:
            rate = int(rate)
            if rate < 50:
                rate = 50  # Minimum rate
            elif rate > 300:
                rate = 300  # Maximum rate
            
            self.voice_rate = rate
            if self.tts_engine:
                self.tts_engine.setProperty('rate', rate)
                print(f"Voice rate set to {rate}")
            return True
        except Exception as e:
            print(f"Error setting voice rate: {str(e)}")
            return False
            
    def set_voice_volume(self, volume):
        """Set the voice volume"""
        try:
            volume = float(volume)
            if volume < 0.0:
                volume = 0.0
            elif volume > 1.0:
                volume = 1.0
                
            self.voice_volume = volume
            if self.tts_engine:
                self.tts_engine.setProperty('volume', volume)
                print(f"Voice volume set to {volume}")
            return True
        except Exception as e:
            print(f"Error setting voice volume: {str(e)}")
            return False
    
    def set_voice_volume(self, volume):
        """Set the speech volume (0.0 to 1.0)"""
        if self.tts_engine:
            try:
                volume = float(volume)
                if volume < 0.0:
                    volume = 0.0
                elif volume > 1.0:
                    volume = 1.0
                
                self.voice_volume = volume
                self.tts_engine.setProperty('volume', volume)
                return True
            except Exception as e:
                print(f"Error setting voice volume: {str(e)}")
        return False
    
    def get_available_voices(self):
        """Get list of all available voices"""
        if self.tts_engine:
            try:
                voices = self.tts_engine.getProperty('voices')
                voice_list = []
                for voice in voices:
                    voice_list.append({
                        'id': voice.id,
                        'name': voice.name,
                        'languages': getattr(voice, 'languages', []),
                        'gender': getattr(voice, 'gender', None)
                    })
                return voice_list
            except Exception as e:
                print(f"Error getting available voices: {str(e)}")
        return []
    
    def get_voices_by_language(self, language=None):
        """Get available voices for a specific language"""
        if language is None:
            language = self.language
            
        if language in self.available_voices:
            # Combine male and female voices
            return self.available_voices[language]["male"] + self.available_voices[language]["female"]
        return []
    
    def get_current_voice_info(self):
        """Get information about the currently selected voice"""
        return {
            'voice': self.selected_voice,
            'language': self.voice_language,
            'gender': self.voice_gender,
            'enabled': self.voice_enabled
        }


class AssistantWidget(QWidget):
    """Widget for displaying and interacting with the Doxly assistant"""
    
    def __init__(self, parent=None, token=None, username=None):
        super().__init__(parent)
        self.token = token
        self.username = username
        self.assistant = DoxlyAssistant()
        self.voice_handler = None
        self.is_listening = False
        
        # Set up the UI
        self.setup_ui()
        
        # Set up reminder checker
        self.reminder_timer = QTimer(self)
        self.reminder_timer.timeout.connect(self.check_reminders)
        self.reminder_timer.start(60000)  # Check every minute
        
        # Set up voice settings menu
        self.setup_voice_settings_menu()
    
    def setup_ui(self):
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Assistant header
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        title = QLabel("Doxly Assistant")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        header_layout.addWidget(title)
        
        # Voice button
        self.voice_btn = QPushButton()
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "icons", "microphone.png")
        if os.path.exists(icon_path):
            self.voice_btn.setIcon(QIcon(icon_path))
        else:
            self.voice_btn.setText("🎤")
        self.voice_btn.setToolTip("Speak to Doxly")
        self.voice_btn.setFixedSize(36, 36)
        self.voice_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                border-radius: 18px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.voice_btn.clicked.connect(self.toggle_voice_input)
        header_layout.addWidget(self.voice_btn)
        
        # Settings button removed as per requirements
        
        main_layout.addWidget(header)
        
        # Conversation display
        self.conversation_area = QScrollArea()
        self.conversation_area.setWidgetResizable(True)
        self.conversation_area.setFrameShape(QFrame.Shape.NoFrame)
        self.conversation_area.setStyleSheet("""
            QScrollArea {
                background-color: #f5f5f5;
                border-radius: 10px;
                border: 1px solid #dcdde1;
            }
        """)
        
        self.conversation_widget = QWidget()
        self.conversation_layout = QVBoxLayout(self.conversation_widget)
        self.conversation_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.conversation_layout.setContentsMargins(10, 10, 10, 10)
        self.conversation_layout.setSpacing(15)
        
        self.conversation_area.setWidget(self.conversation_widget)
        main_layout.addWidget(self.conversation_area, 1)  # 1 = stretch factor
        
        # Input area
        input_container = QWidget()
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(0, 0, 0, 0)
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Ask Doxly something...")
        self.input_field.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border-radius: 20px;
                border: 1px solid #bdc3c7;
                background-color: white;
            }
        """)
        self.input_field.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.input_field)
        
        send_btn = QPushButton("Send")
        send_btn.setIcon(QIcon("assets/icons/send.png"))  # Assuming icon exists
        send_btn.setToolTip("Send message")
        send_btn.setFixedSize(70, 36)  # Wider to accommodate text
        send_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                border-radius: 18px;
                padding: 5px;
                color: black;  /* Make text visible */
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        send_btn.clicked.connect(self.send_message)
        input_layout.addWidget(send_btn)
        
        main_layout.addWidget(input_container)
        
        # Add welcome message
        self.add_assistant_message(random.choice(self.assistant.responses[self.assistant.language]["greeting"]))
    
    def send_message(self):
        """Send a message to the assistant and display the response"""
        user_message = self.input_field.text().strip()
        if not user_message:
            return
        
        # Display user message
        self.add_user_message(user_message)
        
        # Clear input field
        self.input_field.clear()
        
        # Process message and get response
        response = self.assistant.process_query(user_message)
        
        # Display assistant response
        self.add_assistant_message(response)
        
        # Handle special actions if needed
        self.handle_special_actions(user_message, response)
    
    def add_user_message(self, message):
        """Add a user message to the conversation display"""
        message_widget = QFrame()
        message_widget.setStyleSheet("""
            QFrame {
                background-color: #dcf8c6;
                border-radius: 10px;
                padding: 5px;
            }
        """)
        
        message_layout = QVBoxLayout(message_widget)
        message_layout.setContentsMargins(10, 10, 10, 10)
        
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        message_label.setStyleSheet("color: #2c3e50; font-size: 14px;")
        message_layout.addWidget(message_label)
        
        # Add timestamp
        timestamp = QLabel(datetime.datetime.now().strftime("%H:%M"))
        timestamp.setStyleSheet("color: #7f8c8d; font-size: 10px;")
        timestamp.setAlignment(Qt.AlignmentFlag.AlignRight)
        message_layout.addWidget(timestamp)
        
        # Add to conversation with right alignment
        message_container = QHBoxLayout()
        message_container.addStretch()
        message_container.addWidget(message_widget)
        
        self.conversation_layout.addLayout(message_container)
        
        # Scroll to bottom
        self.conversation_area.verticalScrollBar().setValue(
            self.conversation_area.verticalScrollBar().maximum()
        )
    
    def add_assistant_message(self, message):
        """Add an assistant message to the conversation display"""
        message_widget = QFrame()
        message_widget.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 5px;
                border: 1px solid #e0e0e0;
            }
        """)
        
        message_layout = QVBoxLayout(message_widget)
        message_layout.setContentsMargins(10, 10, 10, 10)
        
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        message_label.setStyleSheet("color: #2c3e50; font-size: 14px;")
        message_layout.addWidget(message_label)
        
        # Add timestamp
        timestamp = QLabel(datetime.datetime.now().strftime("%H:%M"))
        timestamp.setStyleSheet("color: #7f8c8d; font-size: 10px;")
        timestamp.setAlignment(Qt.AlignmentFlag.AlignRight)
        message_layout.addWidget(timestamp)
        
        # Add to conversation with left alignment
        message_container = QHBoxLayout()
        message_container.addWidget(message_widget)
        message_container.addStretch()
        
        self.conversation_layout.addLayout(message_container)
        
        # Scroll to bottom
        self.conversation_area.verticalScrollBar().setValue(
            self.conversation_area.verticalScrollBar().maximum()
        )
    
    def setup_voice_settings_menu(self):
        """Set up the voice settings menu"""
        # This will be populated when the settings dialog is shown
        self.language_options = ["English", "Arabic"]
        self.gender_options = ["male", "female"]
    
    def show_settings_dialog(self):
        """Show the assistant settings dialog"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Assistant Settings")
        dialog.setMinimumWidth(350)
        
        layout = QVBoxLayout(dialog)
        
        # Create form layout for settings
        form_layout = QFormLayout()
        form_layout.setContentsMargins(10, 10, 10, 10)
        form_layout.setSpacing(15)
        
        # Language selection
        self.language_combo = QComboBox()
        for lang in self.language_options:
            self.language_combo.addItem(lang)
        
        # Set current language
        current_index = self.language_combo.findText(self.assistant.voice_language)
        if current_index >= 0:
            self.language_combo.setCurrentIndex(current_index)
        
        form_layout.addRow("Voice Language:", self.language_combo)
        
        # Gender selection
        self.gender_combo = QComboBox()
        self.gender_combo.addItem("Male", "male")
        self.gender_combo.addItem("Female", "female")
        
        # Set current gender
        gender_index = 0 if self.assistant.voice_gender == "male" else 1
        self.gender_combo.setCurrentIndex(gender_index)
        
        form_layout.addRow("Voice Gender:", self.gender_combo)
        
        # Voice enabled checkbox
        self.voice_enabled_checkbox = QCheckBox("Enable Voice")
        self.voice_enabled_checkbox.setChecked(self.assistant.voice_enabled)
        form_layout.addRow("", self.voice_enabled_checkbox)
        
        # Voice rate slider
        self.rate_slider = QSlider(Qt.Orientation.Horizontal)
        self.rate_slider.setMinimum(50)
        self.rate_slider.setMaximum(300)
        self.rate_slider.setValue(self.assistant.voice_rate)
        self.rate_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.rate_slider.setTickInterval(50)
        
        rate_container = QWidget()
        rate_layout = QHBoxLayout(rate_container)
        rate_layout.setContentsMargins(0, 0, 0, 0)
        rate_layout.addWidget(self.rate_slider)
        rate_value_label = QLabel(f"{self.assistant.voice_rate}")
        self.rate_slider.valueChanged.connect(lambda v: rate_value_label.setText(f"{v}"))
        rate_layout.addWidget(rate_value_label)
        
        form_layout.addRow("Speech Rate:", rate_container)
        
        # Voice volume slider
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(int(self.assistant.voice_volume * 100))
        self.volume_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.volume_slider.setTickInterval(20)
        
        volume_container = QWidget()
        volume_layout = QHBoxLayout(volume_container)
        volume_layout.setContentsMargins(0, 0, 0, 0)
        volume_layout.addWidget(self.volume_slider)
        volume_value_label = QLabel(f"{int(self.assistant.voice_volume * 100)}%")
        self.volume_slider.valueChanged.connect(lambda v: volume_value_label.setText(f"{v}%"))
        volume_layout.addWidget(volume_value_label)
        
        form_layout.addRow("Volume:", volume_container)
        
        # Test voice button
        test_voice_btn = QPushButton("Test Voice")
        test_voice_btn.clicked.connect(self.test_voice)
        form_layout.addRow("", test_voice_btn)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        cancel_btn = QPushButton("Cancel")
        
        save_btn.clicked.connect(lambda: self.save_voice_settings(dialog))
        cancel_btn.clicked.connect(dialog.reject)
        
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
        dialog.exec()
    
    def test_voice(self):
        """Test the current voice settings"""
        # Get selected language and gender
        language = self.language_combo.currentText()
        gender = self.gender_combo.currentData()
        
        print(f"Testing voice: {language}, {gender}")
        
        # Temporarily set the voice
        original_language = self.assistant.voice_language
        original_gender = self.assistant.voice_gender
        original_rate = self.assistant.voice_rate
        original_volume = self.assistant.voice_volume
        original_enabled = self.assistant.voice_enabled
        
        # Apply test settings
        self.assistant.set_voice_language(language)
        self.assistant.set_voice_gender(gender)
        self.assistant.set_voice_rate(self.rate_slider.value())
        self.assistant.set_voice_volume(self.volume_slider.value() / 100.0)
        self.assistant.set_voice_enabled(self.voice_enabled_checkbox.isChecked())
        
        # Get current voice info for debugging
        voice_info = self.assistant.get_current_voice_info()
        if voice_info['voice']:
            print(f"Selected voice: {voice_info['voice']['name']}")
        
        # Speak test message
        if language == "English":
            self.assistant.speak("This is a test of the voice settings.")
        elif language == "Arabic":
            # Use a longer test phrase for Arabic to ensure it's working
            self.assistant.speak("هذا اختبار لإعدادات الصوت. مرحبا بكم في دوكسلي.")
        else:
            self.assistant.speak("Testing voice settings.")
        
        # Restore original settings
        self.assistant.set_voice_language(original_language)
        self.assistant.set_voice_gender(original_gender)
        self.assistant.set_voice_rate(original_rate)
        self.assistant.set_voice_volume(original_volume)
        self.assistant.set_voice_enabled(original_enabled)
    
    def save_voice_settings(self, dialog):
        """Save the voice settings"""
        # Get values from UI controls
        language = self.language_combo.currentText()
        gender = self.gender_combo.currentData()
        rate = self.rate_slider.value()
        volume = self.volume_slider.value() / 100.0
        enabled = self.voice_enabled_checkbox.isChecked()
        
        # Apply settings
        self.assistant.set_voice_language(language)
        self.assistant.set_voice_gender(gender)
        self.assistant.set_voice_rate(rate)
        self.assistant.set_voice_volume(volume)
        self.assistant.set_voice_enabled(enabled)
        
        # Close dialog
        dialog.accept()
        
        # Show confirmation
        self.add_assistant_message("Voice settings updated.")
        
    def toggle_voice_input(self):
        """Toggle voice input on/off"""
        if self.is_listening:
            # Stop listening
            self.is_listening = False
            self.voice_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    border-radius: 18px;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            
            if self.voice_handler:
                self.voice_handler.is_listening = False
                self.voice_handler.wait()  # Wait for thread to finish properly
                self.voice_handler = None
        else:
            # Start listening
            self.is_listening = True
            self.voice_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    border-radius: 18px;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
            """)
            
            # Initialize voice handler
            try:
                self.voice_handler = VoiceCommandHandler()
                self.voice_handler.command_detected.connect(self.handle_voice_command)
                self.voice_handler.error_occurred.connect(self.handle_voice_error)
                self.voice_handler.start()
                
                # Add listening indicator
                self.add_assistant_message("I'm listening... Speak now.")
            except Exception as e:
                self.add_assistant_message(f"Error initializing voice recognition: {str(e)}")
                self.is_listening = False
                self.voice_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #3498db;
                        border-radius: 18px;
                        padding: 5px;
                    }
                    QPushButton:hover {
                        background-color: #2980b9;
                    }
                """)
    
    def handle_voice_command(self, command):
        """Handle a voice command from the voice handler"""
        # Check if this is a predefined command or free text
        predefined_commands = ["upload", "share", "list", "settings", "logout", 
                              "assistant", "templates", "analysis", "email", "reminder"]
        
        # Display the recognized command to provide feedback to the user
        self.add_user_message(f"Voice command: {command}")
        
        if command in predefined_commands:
            # This is a predefined command that should be handled by the main window
            
            # Get the parent window (main window)
            main_window = self.parent()
            while main_window and not hasattr(main_window, 'switch_page'):
                main_window = main_window.parent()
                
            # If we found the main window, let it handle the command
            if main_window and hasattr(main_window, 'handle_voice_command'):
                main_window.handle_voice_command(command)
                # Add feedback message
                self.add_assistant_message(f"Executing command: {command}")
                return
        
        # For non-predefined commands or if main window handling failed, process as normal query
        self.add_user_message(command)
        
        # Process command and get response
        response = self.assistant.process_query(command)
        
        # Display assistant response
        self.add_assistant_message(response)
        
        # Handle special actions if needed
        action_taken = self.handle_special_actions(command, response)
        
        # If no action was taken and this might be a command, provide feedback
        if not action_taken and any(keyword in command.lower() for keyword in ["open", "show", "go to", "search", "find"]):
            self.add_assistant_message("I understood your request but couldn't perform the action. Please try a different command.")

    
    def process_voice_command(self, command):
        """Process a voice command received from the main window"""
        if not command:
            return
        
        print(f"Passing command to assistant: {command}")
        
        # Display the command as a user message with clear styling
        self.add_user_message(f"Voice command: {command}")
        
        # Process command and get response
        response = self.assistant.process_query(command)
        
        # Display assistant response with clear styling
        self.add_assistant_message(response)
        
        # Handle special actions if needed
        action_taken = self.handle_special_actions(command, response)
        
        # If no action was taken and this might be a command, provide feedback
        if not action_taken and any(keyword in command.lower() for keyword in ["open", "show", "go to", "search", "find"]):
            self.add_assistant_message("I understood your request but couldn't perform the action. Please try a different command.")
        
        # Provide visual feedback that voice processing is complete
        self.is_listening = False
        self.voice_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                border-radius: 18px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        
        return True
    
    def handle_voice_error(self, error_message):
        """Handle voice recognition errors"""
        # Display error with clear styling
        self.add_assistant_message(f"Error: {error_message}")
        
        # Reset listening state
        self.is_listening = False
        self.voice_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                border-radius: 18px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        
        # Stop the voice handler
        if self.voice_handler:
            self.voice_handler.is_listening = False
            
    def toggle_voice_output(self):
        """Toggle voice output on/off"""
        enabled = self.voice_output_btn.isChecked()
        self.assistant.set_voice_enabled(not enabled)  # Toggle the current state
        self.voice_output_btn.setChecked(not enabled)
        
        # Update button appearance
        if not enabled:  # Voice is now enabled
            self.voice_output_btn.setStyleSheet("""
                QPushButton {
                    background-color: #27ae60;
                    border-radius: 18px;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #2ecc71;
                }
            """)
            self.add_assistant_message("Voice output enabled")
            # Speak confirmation
            self.assistant.speak("Voice output enabled")
        else:  # Voice is now disabled
            self.voice_output_btn.setStyleSheet("""
                QPushButton {
                    background-color: #95a5a6;
                    border-radius: 18px;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #7f8c8d;
                }
            """)
            self.add_assistant_message("Voice output disabled")
    
    def show_voice_settings(self):
        """Show dialog with voice settings"""
        dialog = VoiceSettingsDialog(self.assistant, self)
        dialog.exec()
    
    def handle_special_actions(self, user_message, response):
        """Handle special actions based on user message and assistant response"""
        # Get the parent window (main window)
        main_window = self.parent()
        while main_window and not hasattr(main_window, 'switch_page'):
            main_window = main_window.parent()
        
        # Check for special intents that require application actions
        intent, entities = self.assistant._detect_intent(user_message.lower())
        
        # Log the detected intent and entities for debugging
        print(f"Detected intent: {intent}, entities: {entities}")
        
        if intent == "open_settings" and main_window:
            # Open settings page if available
            if hasattr(main_window, 'switch_page'):
                main_window.switch_page("settings")
                self.add_assistant_message("Opening settings for you.")
                return True
                
        elif intent == "document_search" and main_window:
            # Open documents page and perform search
            if hasattr(main_window, 'switch_page'):
                main_window.switch_page("documents")
                search_term = entities[0] if entities else ""
                self.add_assistant_message(f"Searching for documents related to '{search_term}'...")
                # If the documents page has a search method, we would call it here
                # with the search term from entities
                if hasattr(main_window.pages["documents"], 'search_documents') and search_term:
                    try:
                        main_window.pages["documents"].search_documents(search_term)
                    except Exception as e:
                        print(f"Error searching documents: {str(e)}")
                return True
                
        elif intent == "email" and main_window:
            # Open email page
            if hasattr(main_window, 'switch_page'):
                main_window.switch_page("email")
                recipient = entities[0] if entities else ""
                self.add_assistant_message(f"Opening email composer{' to ' + recipient if recipient else ''}...")
                return True
        
        elif intent == "schedule" and main_window:
            # Open calendar or schedule page if available
            if hasattr(main_window, 'switch_page') and "calendar" in main_window.pages:
                main_window.switch_page("calendar")
                self.add_assistant_message("Opening your calendar...")
                return True
                
        elif intent == "reminder" and entities:
            # We've already set the reminder in process_query, just confirm it was handled
            return True
                
        # Check for reminders
        self.check_reminders()
        
        # Return False if no special action was taken
        return False
    
    def check_reminders(self):
        """Check for due reminders and notify the user"""
        due_reminders = self.assistant.check_due_reminders()
        
        for reminder in due_reminders:
            # Display reminder notification
            reminder_message = f"Reminder: {reminder['task']}"
            self.add_assistant_message(reminder_message)
            
            # Also speak the reminder if voice is enabled
            if self.assistant.voice_enabled:
                self.assistant.speak(reminder_message)
            
            # You could also show a system notification here
            # This would depend on the platform (Windows, macOS, etc.)


class VoiceSettingsDialog(QDialog):
    """Dialog for adjusting voice settings"""
    
    def __init__(self, assistant, parent=None):
        super().__init__(parent)
        self.assistant = assistant
        self.setWindowTitle("Voice Settings")
        self.setMinimumSize(400, 300)
        self.setup_ui()
    
    def setup_ui(self):
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("Voice Settings")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(title)
        
        # Form layout for settings
        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(15)
        form_layout.setHorizontalSpacing(20)
        
        # Enable/disable voice
        self.voice_enabled_cb = QCheckBox("Enable voice output")
        self.voice_enabled_cb.setChecked(self.assistant.voice_enabled)
        self.voice_enabled_cb.toggled.connect(self.toggle_voice)
        form_layout.addRow("", self.voice_enabled_cb)
        
        # Voice selection
        self.voice_combo = QComboBox()
        self.populate_voices()
        form_layout.addRow("Voice:", self.voice_combo)
        
        # Speech rate slider
        self.rate_slider = QSlider(Qt.Orientation.Horizontal)
        self.rate_slider.setMinimum(50)
        self.rate_slider.setMaximum(300)
        self.rate_slider.setValue(self.assistant.voice_rate)
        self.rate_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.rate_slider.setTickInterval(50)
        self.rate_slider.valueChanged.connect(self.update_rate)
        
        rate_layout = QHBoxLayout()
        rate_layout.addWidget(QLabel("Slow"))
        rate_layout.addWidget(self.rate_slider)
        rate_layout.addWidget(QLabel("Fast"))
        
        form_layout.addRow("Speech Rate:", rate_layout)
        
        # Current rate value
        self.rate_value = QLabel(f"{self.assistant.voice_rate} WPM")
        form_layout.addRow("", self.rate_value)
        
        # Volume slider
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(int(self.assistant.voice_volume * 100))
        self.volume_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.volume_slider.setTickInterval(20)
        self.volume_slider.valueChanged.connect(self.update_volume)
        
        volume_layout = QHBoxLayout()
        volume_layout.addWidget(QLabel("Quiet"))
        volume_layout.addWidget(self.volume_slider)
        volume_layout.addWidget(QLabel("Loud"))
        
        form_layout.addRow("Volume:", volume_layout)
        
        # Current volume value
        self.volume_value = QLabel(f"{int(self.assistant.voice_volume * 100)}%")
        form_layout.addRow("", self.volume_value)
        
        # Test voice button
        self.test_btn = QPushButton("Test Voice")
        self.test_btn.clicked.connect(self.test_voice)
        form_layout.addRow("", self.test_btn)
        
        layout.addLayout(form_layout)
        
        # Close button
        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.accept)
        layout.addWidget(self.close_btn)
    
    def populate_voices(self):
        """Populate the voice selection combo box"""
        voices = self.assistant.get_available_voices()
        if not voices:
            self.voice_combo.addItem("Default Voice")
            return
        
        for i, voice in enumerate(voices):
            self.voice_combo.addItem(voice['name'], voice['id'])
            
        # Set current voice
        if self.assistant.tts_engine:
            current_voice = self.assistant.tts_engine.getProperty('voice')
            for i in range(self.voice_combo.count()):
                if self.voice_combo.itemData(i) == current_voice:
                    self.voice_combo.setCurrentIndex(i)
                    break
        
        self.voice_combo.currentIndexChanged.connect(self.change_voice)
    
    def toggle_voice(self, enabled):
        """Enable or disable voice output"""
        self.assistant.set_voice_enabled(enabled)
    
    def update_rate(self, value):
        """Update the speech rate"""
        self.assistant.set_voice_rate(value)
        self.rate_value.setText(f"{value} WPM")
    
    def update_volume(self, value):
        """Update the speech volume"""
        volume = value / 100.0
        self.assistant.set_voice_volume(volume)
        self.volume_value.setText(f"{value}%")
    
    def change_voice(self, index):
        """Change the voice"""
        if self.assistant.tts_engine and index >= 0:
            voice_id = self.voice_combo.itemData(index)
            if voice_id:
                self.assistant.tts_engine.setProperty('voice', voice_id)
    
    def test_voice(self):
        """Test the current voice settings"""
        self.assistant.speak("This is a test of the current voice settings. How do I sound?")


class ReminderDialog(QDialog):
    """Dialog for managing reminders"""
    
    def __init__(self, assistant, parent=None):
        super().__init__(parent)
        self.assistant = assistant
        self.setWindowTitle("Reminders")
        self.setMinimumSize(400, 300)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Header label
        header = QLabel("Your Reminders")
        header.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px; color: #2c3e50;")
        layout.addWidget(header)
        
        # Instructions
        instructions = QLabel("Select a reminder to remove it, or add a new one.")
        instructions.setWordWrap(True)
        instructions.setStyleSheet("color: #2c3e50;")
        layout.addWidget(instructions)
        
        # Reminders list
        self.reminders_list = QListWidget()
        self.reminders_list.setStyleSheet("""
            QListWidget {
                background-color: #f5f5f5;
                border-radius: 5px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 8px;
                margin: 2px 0px;
                border-radius: 4px;
                background-color: white;
                color: #2c3e50;
                border: 1px solid #e0e0e0;
            }
            QListWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
        """)
        layout.addWidget(self.reminders_list)
        
        # Add reminder form
        form_frame = QFrame()
        form_frame.setStyleSheet("background-color: #f0f0f0; padding: 10px; border-radius: 5px;")
        form_layout = QFormLayout(form_frame)
        
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("Enter reminder task...")
        self.task_input.setStyleSheet("color: #2c3e50; background-color: white; padding: 5px;")
        task_label = QLabel("Task:")
        task_label.setStyleSheet("color: #2c3e50;")
        form_layout.addRow(task_label, self.task_input)
        
        self.time_input = QLineEdit()
        self.time_input.setPlaceholderText("Time (e.g. 14:30 or 2:30 PM)")
        self.time_input.setStyleSheet("color: #2c3e50; background-color: white; padding: 5px;")
        time_label = QLabel("Time:")
        time_label.setStyleSheet("color: #2c3e50;")
        form_layout.addRow(time_label, self.time_input)
        
        layout.addWidget(form_frame)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        add_btn = QPushButton("Add Reminder")
        add_btn.setStyleSheet("background-color: #27ae60; color: white; padding: 8px 15px;")
        add_btn.clicked.connect(self.add_reminder)
        buttons_layout.addWidget(add_btn)
        
        remove_btn = QPushButton("Remove Selected")
        remove_btn.setStyleSheet("background-color: #e74c3c; color: white; padding: 8px 15px;")
        remove_btn.clicked.connect(self.remove_reminder)
        buttons_layout.addWidget(remove_btn)
        
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet("padding: 8px 15px;")
        close_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(close_btn)
        
        layout.addLayout(buttons_layout)
        
        # Load reminders
        self.load_reminders()
    
    def load_reminders(self):
        """Load reminders from the assistant"""
        self.reminders_list.clear()
        
        active_reminders = self.assistant.get_active_reminders()
        
        if not active_reminders:
            item = QListWidgetItem("No active reminders")
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
            self.reminders_list.addItem(item)
            return
        
        for reminder in active_reminders:
            time_str = reminder["time"].strftime("%Y-%m-%d %H:%M")
            item = QListWidgetItem(f"{time_str} - {reminder['task']}")
            self.reminders_list.addItem(item)
    
    def add_reminder(self):
        """Add a new reminder"""
        task = self.task_input.text().strip()
        time_str = self.time_input.text().strip()
        
        if not task:
            QMessageBox.warning(self, "Missing Information", "Please enter a task for the reminder.")
            return
            
        if not time_str:
            QMessageBox.warning(self, "Missing Information", "Please enter a time for the reminder.")
            return
        
        # Set the reminder
        success = self.assistant._set_reminder(task, time_str)
        
        if success:
            self.task_input.clear()
            self.time_input.clear()
            self.load_reminders()
            QMessageBox.information(self, "Reminder Added", f"Reminder set for {time_str}: {task}")
        else:
            QMessageBox.warning(self, "Error", "Could not set reminder. Please check the time format.")
    
    def remove_reminder(self):
        """Remove the selected reminder"""
        selected_items = self.reminders_list.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "No Selection", "Please select a reminder to remove.")