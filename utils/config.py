"""Configuration management"""
import json
import os
from typing import Any, Dict

class Config:
    """Configuration manager"""
    
    _config_file = "config.json"
    _defaults = {
        'device_name': 'ITG Device',
        'port': 25557,
        'encryption_password': 'itg_remote_default',
        'screen_quality': 85,
        'capture_interval': 0.1,
        'discovery_interval': 2.0,
        'auto_accept': False,
        'debug': False,
    }
    
    def __init__(self):
        """Initialize configuration"""
        self.config = self._defaults.copy()
        self.load()
    
    def load(self):
        """Load configuration from file"""
        if os.path.exists(self._config_file):
            try:
                with open(self._config_file, 'r') as f:
                    file_config = json.load(f)
                    self.config.update(file_config)
            except Exception as e:
                print(f"Failed to load config: {e}")
    
    def save(self):
        """Save configuration to file"""
        try:
            with open(self._config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Failed to save config: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set configuration value
        
        Args:
            key: Configuration key
            value: Configuration value
        """
        self.config[key] = value
    
    def to_dict(self) -> Dict:
        """Get configuration as dictionary
        
        Returns:
            Configuration dictionary
        """
        return self.config.copy()

# Global config instance
config = Config()
