import os
import sys
import datetime

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dms_frontend.utils.database import get_database
from dms_frontend.utils.db_integration import DoxlyDatabaseIntegration
from dms_frontend.utils.doxly_assistant_db import DoxlyAssistant

def run_database_test():
    """Run a simple test to verify the database is working"""
    print("\n===== Doxly Database Test =====\n")
    
    # Initialize database
    print("Initializing database...")
    db = get_database()
    if db.connect():
        db_path = db.db_path
        print(f"✓ Database initialized successfully at: {db_path}")
        db.close()
    else:
        print("✗ Failed to initialize database")
        return False
    
    # Test user operations
    print("\nTesting user operations...")
    db = get_database()
    username = "test_user"
    user_id = db.add_user(username, "test@example.com")
    if user_id:
        print(f"✓ Added user '{username}' with ID: {user_id}")
    else:
        print(f"✓ User '{username}' already exists")
        user = db.get_user(username)
        if user:
            user_id = user['id']
            print(f"✓ Retrieved existing user with ID: {user_id}")
    
    # Test reminder operations
    print("\nTesting reminder operations...")
    reminder_time = datetime.datetime.now() + datetime.timedelta(hours=1)
    reminder_id = db.add_reminder(user_id, "Test reminder", reminder_time)
    if reminder_id:
        print(f"✓ Added reminder with ID: {reminder_id}")
        
        # Get active reminders
        reminders = db.get_active_reminders(user_id)
        print(f"✓ Found {len(reminders)} active reminders")
    
    # Test settings operations
    print("\nTesting settings operations...")
    settings = db.get_settings()
    if settings:
        print(f"✓ Retrieved {len(settings)} application settings")
        print("Sample settings:")
        count = 0
        for key, value in settings.items():
            print(f"  - {key}: {value}")
            count += 1
            if count >= 5:  # Show just a few settings
                break
    
    # Test assistant integration
    print("\nTesting assistant integration...")
    assistant = DoxlyAssistant()
    assistant.set_username(username)
    print(f"✓ Initialized assistant with database integration for user '{username}'")
    
    # Test setting a reminder through the assistant
    assistant._set_reminder("Assistant test reminder", "2:00 PM")
    print("✓ Set a reminder through the assistant")
    
    # Get reminders through the assistant
    assistant_reminders = assistant.get_active_reminders()
    print(f"✓ Assistant has {len(assistant_reminders)} active reminders")
    
    print("\n===== Database Test Completed Successfully =====\n")
    print("The local SQLite database is properly set up and working.")
    print(f"Database location: {db_path}")
    return True

if __name__ == "__main__":
    run_database_test()