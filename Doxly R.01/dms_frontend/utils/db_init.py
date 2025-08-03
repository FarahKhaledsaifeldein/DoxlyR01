import os
import sys
import sqlite3
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.database import DoxlyDatabase, get_database
from utils.db_integration import DoxlyDatabaseIntegration

def initialize_database():
    """Initialize the database with tables and default settings"""
    print("Initializing Doxly local database...")
    db = get_database()
    
    # Check if database was initialized successfully
    if db.connect():
        print(f"Database initialized successfully at: {db.db_path}")
        db.close()
        return True
    else:
        print("Failed to initialize database")
        return False

def add_test_data():
    """Add some test data to the database"""
    print("Adding test data to database...")
    db = get_database()
    
    try:
        # Add test user
        user_id = db.add_user("test_user", "test@example.com", "admin")
        if not user_id:
            print("Failed to add test user")
            return False
            
        print(f"Added test user with ID: {user_id}")
        
        # Add test document
        doc_id = db.add_document(
            name="Test Document", 
            file_path="C:/test/document.docx", 
            uploaded_by=user_id,
            metadata='{"keywords": ["test", "document"], "description": "A test document"}'
        )
        if not doc_id:
            print("Failed to add test document")
            return False
            
        print(f"Added test document with ID: {doc_id}")
        
        # Add test template
        template_id = db.add_template(
            name="Test Template", 
            file_path="C:/test/template.docx", 
            created_by=user_id,
            description="A test template",
            category="Legal"
        )
        if not template_id:
            print("Failed to add test template")
            return False
            
        print(f"Added test template with ID: {template_id}")
        
        # Add test reminder
        import datetime
        reminder_time = datetime.datetime.now() + datetime.timedelta(hours=1)
        reminder_id = db.add_reminder(user_id, "Test reminder", reminder_time)
        if not reminder_id:
            print("Failed to add test reminder")
            return False
            
        print(f"Added test reminder with ID: {reminder_id}")
        
        return True
    except Exception as e:
        print(f"Error adding test data: {e}")
        return False
    finally:
        db.close()

def test_db_integration():
    """Test the database integration with the assistant"""
    print("Testing database integration...")
    
    # Create integration with test user
    db_integration = DoxlyDatabaseIntegration("test_user")
    
    # Test getting reminders
    reminders = db_integration.get_active_reminders()
    print(f"Found {len(reminders)} active reminders")
    
    # Test getting settings
    settings = db_integration.get_assistant_settings()
    print("Assistant settings:")
    for key, value in settings.items():
        print(f"  {key}: {value}")
    
    return True

def main():
    """Main function to initialize database and add test data"""
    if initialize_database():
        print("Database initialization successful")
        
        # Add test data if requested
        if len(sys.argv) > 1 and sys.argv[1] == "--with-test-data":
            if add_test_data():
                print("Test data added successfully")
                test_db_integration()
            else:
                print("Failed to add test data")
    else:
        print("Database initialization failed")

if __name__ == "__main__":
    main()