import os
import sys
import sqlite3
import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.database import get_database
from utils.db_integration import DoxlyDatabaseIntegration
from utils.doxly_assistant_db import DoxlyAssistant

def display_separator():
    """Display a separator line for better readability"""
    print("\n" + "-" * 50 + "\n")

def initialize_database():
    """Initialize the database and return its path"""
    print("Initializing Doxly local database...")
    db = get_database()
    
    if db.connect():
        print(f"Database initialized successfully at: {db.db_path}")
        db.close()
        return db.db_path
    else:
        print("Failed to initialize database")
        return None

def test_user_operations():
    """Test user-related database operations"""
    print("\nTesting user operations...")
    db = get_database()
    
    # Add a test user
    user_id = db.add_user("test_user", "test@example.com", "admin")
    print(f"Added user with ID: {user_id}")
    
    # Get the user
    user = db.get_user("test_user")
    print(f"Retrieved user: {user['username']} ({user['email']})")
    
    # Update user preferences
    preferences = {
        "theme": "dark",
        "notifications": True,
        "sidebar_collapsed": False
    }
    db.update_user_preferences("test_user", preferences)
    print("Updated user preferences")
    
    # Get updated user
    updated_user = db.get_user("test_user")
    print(f"User preferences: {updated_user['preferences']}")

def test_document_operations():
    """Test document-related database operations"""
    print("\nTesting document operations...")
    db = get_database()
    
    # Get test user ID
    user = db.get_user("test_user")
    user_id = user['id']
    
    # Add a test document
    doc_id = db.add_document(
        name="Sample Contract", 
        file_path="C:/Users/Documents/sample_contract.docx", 
        uploaded_by=user_id,
        metadata={"type": "contract", "client": "Acme Corp", "status": "draft"}
    )
    print(f"Added document with ID: {doc_id}")
    
    # Get the document
    document = db.get_document(document_id=doc_id)
    print(f"Retrieved document: {document['name']} (Version: {document['version']})")
    
    # Search for documents
    search_results = db.search_documents("contract")
    print(f"Found {len(search_results)} documents matching 'contract'")

def test_reminder_operations():
    """Test reminder-related database operations"""
    print("\nTesting reminder operations...")
    db = get_database()
    
    # Get test user ID
    user = db.get_user("test_user")
    user_id = user['id']
    
    # Add reminders
    now = datetime.datetime.now()
    
    # Reminder for 1 hour from now
    reminder1_time = now + datetime.timedelta(hours=1)
    reminder1_id = db.add_reminder(user_id, "Review contract draft", reminder1_time)
    print(f"Added reminder for 1 hour from now, ID: {reminder1_id}")
    
    # Reminder for tomorrow
    reminder2_time = now + datetime.timedelta(days=1)
    reminder2_id = db.add_reminder(user_id, "Client meeting preparation", reminder2_time)
    print(f"Added reminder for tomorrow, ID: {reminder2_id}")
    
    # Get active reminders
    active_reminders = db.get_active_reminders(user_id)
    print(f"Found {len(active_reminders)} active reminders")
    for reminder in active_reminders:
        print(f"  - {reminder['task']} at {reminder['reminder_time']}")

def test_settings_operations():
    """Test settings-related database operations"""
    print("\nTesting settings operations...")
    db = get_database()
    
    # Get all settings
    all_settings = db.get_settings()
    print("Current settings:")
    for key, value in all_settings.items():
        print(f"  {key}: {value}")
    
    # Update a setting
    db.update_setting("theme", "Dark")
    print("Updated theme setting to 'Dark'")
    
    # Get application settings
    app_settings = db.get_settings("application")
    print("Application settings:")
    for key, value in app_settings.items():
        print(f"  {key}: {value}")

def test_assistant_integration():
    """Test integration with DoxlyAssistant"""
    print("\nTesting DoxlyAssistant integration...")
    
    # Create assistant
    assistant = DoxlyAssistant()
    
    # Set username to initialize database integration
    assistant.set_username("test_user")
    print("Initialized assistant with database integration")
    
    # Set a reminder
    assistant._set_reminder("Call client about contract", "3:00 PM")
    print("Set a reminder through assistant")
    
    # Get active reminders
    reminders = assistant.get_active_reminders()
    print(f"Assistant has {len(reminders)} active reminders:")
    for reminder in reminders:
        print(f"  - {reminder['task']} at {reminder['time'].strftime('%Y-%m-%d %H:%M')}")
    
    # Change assistant settings
    assistant.set_language("English")
    assistant.set_voice_enabled(True)
    assistant.set_voice_rate(160)
    print("Updated assistant settings")

def main():
    """Main function to demonstrate database functionality"""
    print("Doxly Local Database Demo")
    display_separator()
    
    # Initialize database
    db_path = initialize_database()
    if not db_path:
        print("Database initialization failed. Exiting.")
        return
    
    display_separator()
    print(f"Database location: {db_path}")
    display_separator()
    
    # Run tests based on command line arguments
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg == "--users":
            test_user_operations()
        elif arg == "--documents":
            test_document_operations()
        elif arg == "--reminders":
            test_reminder_operations()
        elif arg == "--settings":
            test_settings_operations()
        elif arg == "--assistant":
            test_assistant_integration()
        elif arg == "--all":
            test_user_operations()
            display_separator()
            test_document_operations()
            display_separator()
            test_reminder_operations()
            display_separator()
            test_settings_operations()
            display_separator()
            test_assistant_integration()
    else:
        # Default: run all tests
        test_user_operations()
        display_separator()
        test_document_operations()
        display_separator()
        test_reminder_operations()
        display_separator()
        test_settings_operations()
        display_separator()
        test_assistant_integration()
    
    display_separator()
    print("Database demo completed successfully!")
    print("You can now integrate the database with your Doxly application.")

if __name__ == "__main__":
    main()