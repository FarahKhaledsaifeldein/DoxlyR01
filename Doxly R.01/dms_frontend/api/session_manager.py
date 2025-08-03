import pickle
import os
from typing import Optional

class SessionManager:
    SESSION_FILE = ".session"

    @classmethod
    def save_session(cls, token: str):
        """Save token to file"""
        with open(cls.SESSION_FILE, 'wb') as f:
            pickle.dump({'token': token}, f)

    @classmethod
    def load_session(cls) -> Optional[str]:
        """Load token from file if exists"""
        if os.path.exists(cls.SESSION_FILE):
            with open(cls.SESSION_FILE, 'rb') as f:
                try:
                    return pickle.load(f).get('token')
                except:
                    return None
        return None

    @classmethod
    def clear_session(cls):
        """Remove session file"""
        if os.path.exists(cls.SESSION_FILE):
            os.remove(cls.SESSION_FILE)