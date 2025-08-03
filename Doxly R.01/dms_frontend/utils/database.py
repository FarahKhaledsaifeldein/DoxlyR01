import os
import sqlite3
import datetime
import json
from pathlib import Path

class DoxlyDatabase:
    """SQLite database manager for the Doxly application"""
    
    def __init__(self, db_path=None):
        """Initialize the database connection"""
        if db_path is None:
            # Create database in user's home directory to ensure write permissions
            home_dir = os.path.expanduser("~")
            doxly_dir = os.path.join(home_dir, ".doxly")
            
            # Create directory if it doesn't exist
            os.makedirs(doxly_dir, exist_ok=True)
            
            # Set database path
            db_path = os.path.join(doxly_dir, "doxly_local.db")
        
        self.db_path = db_path
        self.conn = None
        self.cursor = None
    
    def connect(self):
        """Connect to the SQLite database"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            # Enable foreign key constraints
            self.conn.execute("PRAGMA foreign_keys = ON")
            # Return dictionary-like rows
            self.conn.row_factory = sqlite3.Row
            self.cursor = self.conn.cursor()
            return True
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")
            return False
    
    def close(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None
    
    def initialize_database(self):
        """Create all required tables if they don't exist"""
        if not self.connect():
            return False
        
        try:
            # Create users table
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE,
                role TEXT DEFAULT 'viewer',
                last_login TIMESTAMP,
                preferences TEXT,  -- JSON string for user preferences
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # Create documents table
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                reference_code TEXT UNIQUE NOT NULL,
                file_path TEXT NOT NULL,
                version INTEGER DEFAULT 1,
                uploaded_by INTEGER,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_encrypted BOOLEAN DEFAULT 0,
                metadata TEXT,  -- JSON string for additional metadata
                FOREIGN KEY (uploaded_by) REFERENCES users(id)
            )
            ''')
            
            # Create document_versions table
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS document_versions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id INTEGER NOT NULL,
                version INTEGER NOT NULL,
                file_path TEXT NOT NULL,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE,
                UNIQUE(document_id, version)
            )
            ''')
            
            # Create templates table
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                file_path TEXT NOT NULL,
                category TEXT,
                created_by INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (created_by) REFERENCES users(id)
            )
            ''')
            
            # Create reminders table
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                task TEXT NOT NULL,
                reminder_time TIMESTAMP NOT NULL,
                completed BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            ''')
            
            # Create email_messages table
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS email_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender_id INTEGER NOT NULL,
                recipient TEXT NOT NULL,
                subject TEXT,
                body TEXT,
                sent_at TIMESTAMP,
                status TEXT DEFAULT 'draft',  -- draft, sent, failed
                document_id INTEGER,  -- Optional reference to attached document
                FOREIGN KEY (sender_id) REFERENCES users(id),
                FOREIGN KEY (document_id) REFERENCES documents(id)
            )
            ''')
            
            # Create settings table
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                value TEXT,
                category TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # Create document_tags table for document categorization
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS document_tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id INTEGER NOT NULL,
                tag TEXT NOT NULL,
                FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE,
                UNIQUE(document_id, tag)
            )
            ''')
            
            # Create search_history table
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS search_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                query TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            ''')
            
            # Create indexes for performance
            self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_documents_name ON documents(name)')
            self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_documents_reference ON documents(reference_code)')
            self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_reminders_time ON reminders(reminder_time)')
            self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_reminders_user ON reminders(user_id)')
            self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_document_tags ON document_tags(document_id, tag)')
            
            # Insert default settings
            self._insert_default_settings()
            
            self.conn.commit()
            return True
            
        except sqlite3.Error as e:
            print(f"Database initialization error: {e}")
            self.conn.rollback()
            return False
        finally:
            self.close()
    
    def _insert_default_settings(self):
        """Insert default application settings"""
        default_settings = [
            ('language', 'English', 'application'),
            ('theme', 'Light', 'application'),
            ('default_save_location', os.path.join(os.path.expanduser("~"), "Documents", "Doxly"), 'file_handling'),
            ('default_export_format', 'PDF', 'file_handling'),
            ('compress_files', '1', 'file_handling'),
            ('voice_enabled', '1', 'voice_assistant'),
            ('voice_rate', '150', 'voice_assistant'),
            ('voice_volume', '1.0', 'voice_assistant'),
            ('voice_language', 'English', 'voice_assistant'),
            ('voice_gender', 'female', 'voice_assistant'),
            ('check_updates', '1', 'application')
        ]
        
        for key, value, category in default_settings:
            # Use INSERT OR IGNORE to avoid duplicates
            self.cursor.execute(
                'INSERT OR IGNORE INTO settings (key, value, category) VALUES (?, ?, ?)',
                (key, value, category)
            )
    
    # User management methods
    def add_user(self, username, email=None, role='viewer', preferences=None):
        """Add a new user to the database"""
        if not self.connect():
            return False
        
        try:
            if preferences:
                preferences_json = json.dumps(preferences)
            else:
                preferences_json = json.dumps({})
                
            self.cursor.execute(
                'INSERT INTO users (username, email, role, preferences) VALUES (?, ?, ?, ?)',
                (username, email, role, preferences_json)
            )
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error adding user: {e}")
            self.conn.rollback()
            return False
        finally:
            self.close()
    
    def get_user(self, username):
        """Get user by username"""
        if not self.connect():
            return None
        
        try:
            self.cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
            user = self.cursor.fetchone()
            if user:
                return dict(user)
            return None
        except sqlite3.Error as e:
            print(f"Error getting user: {e}")
            return None
        finally:
            self.close()
    
    def update_user_preferences(self, username, preferences):
        """Update user preferences"""
        if not self.connect():
            return False
        
        try:
            preferences_json = json.dumps(preferences)
            self.cursor.execute(
                'UPDATE users SET preferences = ? WHERE username = ?',
                (preferences_json, username)
            )
            self.conn.commit()
            return self.cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error updating user preferences: {e}")
            self.conn.rollback()
            return False
        finally:
            self.close()
    
    # Document management methods
    def add_document(self, name, file_path, uploaded_by, reference_code=None, version=1, is_encrypted=False, metadata=None):
        """Add a new document to the database"""
        if not self.connect():
            return False
        
        try:
            if reference_code is None:
                import uuid
                reference_code = str(uuid.uuid4())
                
            if metadata:
                metadata_json = json.dumps(metadata)
            else:
                metadata_json = json.dumps({})
                
            self.cursor.execute(
                '''INSERT INTO documents 
                   (name, reference_code, file_path, version, uploaded_by, is_encrypted, metadata) 
                   VALUES (?, ?, ?, ?, ?, ?, ?)''',
                (name, reference_code, file_path, version, uploaded_by, is_encrypted, metadata_json)
            )
            document_id = self.cursor.lastrowid
            
            # Also add to document_versions
            self.cursor.execute(
                'INSERT INTO document_versions (document_id, version, file_path) VALUES (?, ?, ?)',
                (document_id, version, file_path)
            )
            
            self.conn.commit()
            return document_id
        except sqlite3.Error as e:
            print(f"Error adding document: {e}")
            self.conn.rollback()
            return False
        finally:
            self.close()
    
    def get_document(self, document_id=None, reference_code=None):
        """Get document by ID or reference code"""
        if not self.connect():
            return None
        
        try:
            if document_id:
                self.cursor.execute('SELECT * FROM documents WHERE id = ?', (document_id,))
            elif reference_code:
                self.cursor.execute('SELECT * FROM documents WHERE reference_code = ?', (reference_code,))
            else:
                return None
                
            document = self.cursor.fetchone()
            if document:
                return dict(document)
            return None
        except sqlite3.Error as e:
            print(f"Error getting document: {e}")
            return None
        finally:
            self.close()
    
    def search_documents(self, query, limit=20):
        """Search documents by name or metadata"""
        if not self.connect():
            return []
        
        try:
            search_term = f"%{query}%"
            self.cursor.execute(
                '''SELECT * FROM documents 
                   WHERE name LIKE ? OR metadata LIKE ? 
                   ORDER BY uploaded_at DESC LIMIT ?''',
                (search_term, search_term, limit)
            )
            documents = self.cursor.fetchall()
            return [dict(doc) for doc in documents]
        except sqlite3.Error as e:
            print(f"Error searching documents: {e}")
            return []
        finally:
            self.close()
    
    # Template management methods
    def add_template(self, name, file_path, created_by, description=None, category=None):
        """Add a new template to the database"""
        if not self.connect():
            return False
        
        try:
            self.cursor.execute(
                'INSERT INTO templates (name, description, file_path, category, created_by) VALUES (?, ?, ?, ?, ?)',
                (name, description, file_path, category, created_by)
            )
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error adding template: {e}")
            self.conn.rollback()
            return False
        finally:
            self.close()
    
    def get_templates(self, category=None):
        """Get all templates, optionally filtered by category"""
        if not self.connect():
            return []
        
        try:
            if category:
                self.cursor.execute('SELECT * FROM templates WHERE category = ?', (category,))
            else:
                self.cursor.execute('SELECT * FROM templates')
                
            templates = self.cursor.fetchall()
            return [dict(template) for template in templates]
        except sqlite3.Error as e:
            print(f"Error getting templates: {e}")
            return []
        finally:
            self.close()
    
    # Reminder management methods
    def add_reminder(self, user_id, task, reminder_time):
        """Add a new reminder to the database"""
        if not self.connect():
            return False
        
        try:
            # Convert reminder_time to string if it's a datetime object
            if isinstance(reminder_time, datetime.datetime):
                reminder_time = reminder_time.isoformat()
                
            self.cursor.execute(
                'INSERT INTO reminders (user_id, task, reminder_time) VALUES (?, ?, ?)',
                (user_id, task, reminder_time)
            )
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error adding reminder: {e}")
            self.conn.rollback()
            return False
        finally:
            self.close()
    
    def get_active_reminders(self, user_id):
        """Get all active (non-completed) reminders for a user"""
        if not self.connect():
            return []
        
        try:
            now = datetime.datetime.now().isoformat()
            self.cursor.execute(
                '''SELECT * FROM reminders 
                   WHERE user_id = ? AND completed = 0 AND reminder_time > ? 
                   ORDER BY reminder_time''',
                (user_id, now)
            )
            reminders = self.cursor.fetchall()
            return [dict(reminder) for reminder in reminders]
        except sqlite3.Error as e:
            print(f"Error getting active reminders: {e}")
            return []
        finally:
            self.close()
    
    def get_due_reminders(self, user_id):
        """Get all due reminders for a user"""
        if not self.connect():
            return []
        
        try:
            now = datetime.datetime.now().isoformat()
            self.cursor.execute(
                '''SELECT * FROM reminders 
                   WHERE user_id = ? AND completed = 0 AND reminder_time <= ? 
                   ORDER BY reminder_time''',
                (user_id, now)
            )
            reminders = self.cursor.fetchall()
            
            # Mark these reminders as completed
            if reminders:
                reminder_ids = [r['id'] for r in reminders]
                placeholders = ','.join(['?'] * len(reminder_ids))
                self.cursor.execute(
                    f'UPDATE reminders SET completed = 1 WHERE id IN ({placeholders})',
                    reminder_ids
                )
                self.conn.commit()
                
            return [dict(reminder) for reminder in reminders]
        except sqlite3.Error as e:
            print(f"Error getting due reminders: {e}")
            return []
        finally:
            self.close()
    
    # Settings management methods
    def get_settings(self, category=None):
        """Get all settings, optionally filtered by category"""
        if not self.connect():
            return {}
        
        try:
            if category:
                self.cursor.execute('SELECT key, value FROM settings WHERE category = ?', (category,))
            else:
                self.cursor.execute('SELECT key, value FROM settings')
                
            settings = self.cursor.fetchall()
            return {row['key']: row['value'] for row in settings}
        except sqlite3.Error as e:
            print(f"Error getting settings: {e}")
            return {}
        finally:
            self.close()
    
    def update_setting(self, key, value):
        """Update a setting value"""
        if not self.connect():
            return False
        
        try:
            self.cursor.execute(
                'UPDATE settings SET value = ?, updated_at = CURRENT_TIMESTAMP WHERE key = ?',
                (value, key)
            )
            self.conn.commit()
            return self.cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error updating setting: {e}")
            self.conn.rollback()
            return False
        finally:
            self.close()
    
    # Email management methods
    def add_email(self, sender_id, recipient, subject=None, body=None, document_id=None):
        """Add a new email draft to the database"""
        if not self.connect():
            return False
        
        try:
            self.cursor.execute(
                '''INSERT INTO email_messages 
                   (sender_id, recipient, subject, body, document_id, status) 
                   VALUES (?, ?, ?, ?, ?, ?)''',
                (sender_id, recipient, subject, body, document_id, 'draft')
            )
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error adding email: {e}")
            self.conn.rollback()
            return False
        finally:
            self.close()
    
    def update_email_status(self, email_id, status, sent_at=None):
        """Update email status (draft, sent, failed)"""
        if not self.connect():
            return False
        
        try:
            if sent_at is None and status == 'sent':
                sent_at = datetime.datetime.now().isoformat()
                
            self.cursor.execute(
                'UPDATE email_messages SET status = ?, sent_at = ? WHERE id = ?',
                (status, sent_at, email_id)
            )
            self.conn.commit()
            return self.cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error updating email status: {e}")
            self.conn.rollback()
            return False
        finally:
            self.close()


# Helper function to get database instance
def get_database():
    """Get a configured database instance"""
    db = DoxlyDatabase()
    # Initialize database if needed
    db.initialize_database()
    return db