import speech_recognition as sr
from PyQt6.QtCore import QThread, pyqtSignal

class VoiceCommandHandler(QThread):
    command_detected = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.recognizer = sr.Recognizer()
        self.is_listening = True
        # Expanded command dictionary with more variations
        self.commands = {
            "upload": ["upload document", "upload file", "new document", "add document", "create document"],
            "share": ["share document", "share file", "send document"],
            "list": ["show documents", "list documents", "my documents", "view documents"],
            "settings": ["open settings", "show settings", "go to settings", "change settings"],
            "logout": ["logout", "sign out", "exit", "log out"],
            "assistant": ["open assistant", "show assistant", "hey doxly", "assistant"],
            "templates": ["show templates", "open templates", "go to templates"],
            "analysis": ["show analysis", "open analysis", "analytics", "show analytics"],
            "email": ["open email", "show email", "compose email", "new email"],
            "reminder": ["set reminder", "create reminder", "add reminder", "new reminder"]
        }

    def run(self):
        try:
            # Test microphone initialization first
            sr.Microphone()
        except OSError as e:
            self.error_occurred.emit("Error: Could not initialize microphone. Please check your audio settings.")
            return
        except Exception as e:
            self.error_occurred.emit(f"Error: {str(e)}")
            return

        while self.is_listening:
            try:
                with sr.Microphone() as source:
                    print("Listening for voice commands...")
                    self.recognizer.adjust_for_ambient_noise(source)
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                    
                    # Try to recognize speech
                    try:
                        # Try Google's speech recognition service first
                        text = self.recognizer.recognize_google(audio, language='en-US')
                        print(f"Recognized text: {text}")
                        
                        # Process the recognized text
                        command_text = text.lower()
                        command_found = False
                        
                        # Check if the text matches any of our defined commands
                        for action, phrases in self.commands.items():
                            if any(phrase in command_text for phrase in phrases):
                                print(f"Command detected: {action}")
                                self.command_detected.emit(action)
                                command_found = True
                                break
                        
                        # If no command was found, pass the raw text to the assistant
                        if not command_found:
                            print(f"No predefined command found, passing to assistant: {command_text}")
                            self.command_detected.emit(command_text)
                            
                    except sr.UnknownValueError:
                        # Speech was unintelligible
                        print("Could not understand audio")
                        continue
                    except sr.RequestError as e:
                        # API was unreachable or unresponsive
                        print(f"Google Speech Recognition service error: {e}")
                        
                        # Try offline recognition as fallback
                        try:
                            text = self.recognizer.recognize_sphinx(audio, language='en-US')
                            print(f"Sphinx recognized: {text}")
                            
                            # Process with offline recognition
                            command_text = text.lower()
                            command_found = False
                            
                            for action, phrases in self.commands.items():
                                if any(phrase in command_text for phrase in phrases):
                                    self.command_detected.emit(action)
                                    command_found = True
                                    break
                            
                            if not command_found:
                                self.command_detected.emit(command_text)
                                
                        except Exception as sphinx_error:
                            print(f"Sphinx error: {sphinx_error}")
                            self.error_occurred.emit("Speech recognition failed: Both online and offline recognition failed")
                            continue
            except sr.WaitTimeoutError:
                # Timeout waiting for speech
                print("Listening timeout - no speech detected")
                continue
            except sr.UnknownValueError:
                pass
            except sr.RequestError as e:
                self.error_occurred.emit(f"Could not request results: {str(e)}")
            except Exception as e:
                self.error_occurred.emit(f"Error: {str(e)}")

    def stop(self):
        """Stop the voice command handler and cleanup resources"""
        print("Stopping voice command handler")
        self.is_listening = False
        
        # Give the thread time to finish its current operation
        try:
            self.wait(2000)  # Wait up to 2 seconds for thread to finish
            print("Voice command handler stopped successfully")
        except Exception as e:
            print(f"Error stopping voice command handler: {e}")
            # If waiting fails, terminate as a last resort
            self.terminate()
            print("Voice command handler terminated")
            
        # Clean up any resources
        self.recognizer = None