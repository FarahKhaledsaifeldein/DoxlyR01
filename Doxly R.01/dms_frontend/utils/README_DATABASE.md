# Doxly Local Database Implementation

This document provides an overview of the local SQLite database implementation for the Doxly application.

## Overview

The Doxly application now includes a local SQLite database to store and manage:
- User information and preferences
- Document metadata and references
- Document templates
- Reminders
- Email messages
- Application settings

The database is designed to work seamlessly with the existing Doxly assistant and application components.

## Database Structure

The database consists of the following tables:

1. **users** - Stores user information and preferences
2. **documents** - Stores document metadata and file references
3. **document_versions** - Tracks document version history
4. **templates** - Stores document templates
5. **reminders** - Stores user reminders
6. **email_messages** - Stores email drafts and sent messages
7. **settings** - Stores application settings
8. **document_tags** - Stores document categorization tags
9. **search_history** - Tracks user search history

## Implementation Files

- `database.py` - Core database implementation with SQLite
- `db_integration.py` - Integration layer between the database and Doxly assistant
- `doxly_assistant_db.py` - Enhanced version of DoxlyAssistant with database support
- `db_init.py` - Database initialization script
- `db_main.py` - Demo script to test database functionality

## How to Use

### Initializing the Database

The database is automatically initialized when needed. By default, it's created in the user's home directory under `.doxly/doxly_local.db` to ensure write permissions.

```python
from utils.database import get_database

# Get a database instance (creates the database if it doesn't exist)
db = get_database()
```

### Integrating with DoxlyAssistant

The DoxlyAssistant class has been enhanced to work with the database. When a username is set, it automatically initializes the database connection:

```python
from utils.doxly_assistant_db import DoxlyAssistant

# Create assistant
assistant = DoxlyAssistant()

# Set username to initialize database integration
assistant.set_username("test_user")
```

### Working with Reminders

Reminders are now stored in the database, allowing them to persist between application sessions:

```python
# Set a reminder
assistant._set_reminder("Review contract", "3:00 PM")

# Get active reminders
reminders = assistant.get_active_reminders()

# Check for due reminders
due_reminders = assistant.check_due_reminders()
```

### Managing Settings

Application settings are stored in the database and can be accessed or modified:

```python
# Using the database directly
db = get_database()
settings = db.get_settings("voice_assistant")
db.update_setting("voice_enabled", "1")

# Using the assistant
assistant.set_voice_enabled(True)
assistant.set_language("English")
```

## Running the Demo

To test the database functionality, run the `db_main.py` script:

```
python -m dms_frontend.utils.db_main
```

You can also run specific tests:

```
python -m dms_frontend.utils.db_main --users     # Test user operations
python -m dms_frontend.utils.db_main --documents  # Test document operations
python -m dms_frontend.utils.db_main --reminders  # Test reminder operations
python -m dms_frontend.utils.db_main --settings   # Test settings operations
python -m dms_frontend.utils.db_main --assistant  # Test assistant integration
python -m dms_frontend.utils.db_main --all        # Run all tests
```

## Integration Notes

1. The database is designed to work with the existing application without requiring major changes to the codebase.

2. The `DoxlyAssistant` class has been enhanced with database integration, but maintains backward compatibility with the original implementation.

3. For production use, consider implementing proper error handling and transaction management for database operations.

4. The database is stored in the user's home directory to ensure write permissions, but this location can be customized in the `DoxlyDatabase` constructor.

5. The database schema includes indexes for performance optimization on frequently queried fields.