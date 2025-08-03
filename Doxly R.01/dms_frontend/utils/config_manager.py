import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

class ConfigManager:
    """
    A configuration manager for the Doxly application.
    Handles saving and loading settings to/from a JSON file.
    """
    
    def __init__(self, config_dir: Optional[str] = None, config_file: str = "settings.json"):
        """
        Initialize the ConfigManager.
        
        Args:
            config_dir: Directory to store configuration files. If None, uses user's home directory.
            config_file: Name of the configuration file.
        """
        if config_dir is None:
            # Use user's home directory by default
            self.config_dir = os.path.join(str(Path.home()), ".doxly")
        else:
            self.config_dir = config_dir
            
        # Ensure config directory exists
        os.makedirs(self.config_dir, exist_ok=True)
        
        self.config_file = os.path.join(self.config_dir, config_file)
        self.config = {}
        self.default_config = {}
        self.logger = logging.getLogger(__name__)
    
    def set_defaults(self, defaults: Dict[str, Any]) -> None:
        """
        Set default configuration values.
        
        Args:
            defaults: Dictionary of default configuration values.
        """
        self.default_config = defaults
        
        # Apply defaults to current config for any missing keys
        for key, value in defaults.items():
            if key not in self.config:
                self.config[key] = value
    
    def load(self) -> Dict[str, Any]:
        """
        Load configuration from file.
        
        Returns:
            The loaded configuration dictionary.
        """
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
                self.logger.info(f"Configuration loaded from {self.config_file}")
            else:
                self.logger.info(f"No configuration file found at {self.config_file}, using defaults")
                self.config = self.default_config.copy()
        except Exception as e:
            self.logger.error(f"Error loading configuration: {str(e)}")
            self.config = self.default_config.copy()
        
        return self.config
    
    def save(self) -> bool:
        """
        Save current configuration to file.
        
        Returns:
            True if successful, False otherwise.
        """
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
            self.logger.info(f"Configuration saved to {self.config_file}")
            return True
        except Exception as e:
            self.logger.error(f"Error saving configuration: {str(e)}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: The configuration key to retrieve.
            default: Default value to return if key is not found.
            
        Returns:
            The configuration value or default if not found.
        """
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value.
        
        Args:
            key: The configuration key to set.
            value: The value to set.
        """
        self.config[key] = value
    
    def update(self, config_dict: Dict[str, Any]) -> None:
        """
        Update multiple configuration values at once.
        
        Args:
            config_dict: Dictionary of configuration values to update.
        """
        self.config.update(config_dict)
    
    def reset(self) -> None:
        """
        Reset configuration to default values.
        """
        self.config = self.default_config.copy()
        self.logger.info("Configuration reset to defaults")
    
    def reset_key(self, key: str) -> None:
        """
        Reset a specific configuration key to its default value.
        
        Args:
            key: The configuration key to reset.
        """
        if key in self.default_config:
            self.config[key] = self.default_config[key]
            self.logger.info(f"Configuration key '{key}' reset to default")
        else:
            # If no default exists, remove the key
            if key in self.config:
                del self.config[key]
                self.logger.info(f"Configuration key '{key}' removed (no default)")