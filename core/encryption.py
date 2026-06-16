"""Encryption module using AES-256"""
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
import base64

class EncryptionManager:
    """Manages AES-256 encryption and decryption"""
    
    def __init__(self, password: str = None):
        """Initialize encryption manager
        
        Args:
            password: Password for key derivation (optional)
        """
        if password:
            self.key = self._derive_key(password)
        else:
            self.key = Fernet.generate_key()
        self.cipher = Fernet(self.key)
    
    @staticmethod
    def _derive_key(password: str) -> bytes:
        """Derive encryption key from password
        
        Args:
            password: Password string
            
        Returns:
            Derived key suitable for Fernet
        """
        salt = b'itg_remote_salt_'  # Fixed salt for consistency
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    def encrypt(self, data: bytes) -> bytes:
        """Encrypt data using Fernet
        
        Args:
            data: Data to encrypt
            
        Returns:
            Encrypted data
        """
        return self.cipher.encrypt(data)
    
    def decrypt(self, encrypted_data: bytes) -> bytes:
        """Decrypt data using Fernet
        
        Args:
            encrypted_data: Encrypted data
            
        Returns:
            Decrypted data
        """
        try:
            return self.cipher.decrypt(encrypted_data)
        except Exception as e:
            raise ValueError(f"Decryption failed: {str(e)}")
    
    def encrypt_string(self, text: str) -> str:
        """Encrypt string and return base64 encoded result
        
        Args:
            text: Text to encrypt
            
        Returns:
            Base64 encoded encrypted text
        """
        encrypted = self.encrypt(text.encode())
        return base64.b64encode(encrypted).decode()
    
    def decrypt_string(self, encrypted_text: str) -> str:
        """Decrypt base64 encoded string
        
        Args:
            encrypted_text: Base64 encoded encrypted text
            
        Returns:
            Decrypted text
        """
        encrypted = base64.b64decode(encrypted_text.encode())
        decrypted = self.decrypt(encrypted)
        return decrypted.decode()
    
    def get_key(self) -> str:
        """Get encryption key as base64 string
        
        Returns:
            Base64 encoded key
        """
        return self.key.decode()


class SecureConnection:
    """Manages secure communication with encryption"""
    
    def __init__(self, encryption_manager: EncryptionManager):
        """Initialize secure connection
        
        Args:
            encryption_manager: EncryptionManager instance
        """
        self.encryption = encryption_manager
    
    def prepare_message(self, message: dict) -> bytes:
        """Prepare message for transmission with encryption
        
        Args:
            message: Message dictionary
            
        Returns:
            Encrypted message bytes
        """
        import json
        json_str = json.dumps(message)
        return self.encryption.encrypt(json_str.encode())
    
    def process_message(self, encrypted_message: bytes) -> dict:
        """Process received encrypted message
        
        Args:
            encrypted_message: Encrypted message bytes
            
        Returns:
            Decrypted message dictionary
        """
        import json
        decrypted = self.encryption.decrypt(encrypted_message)
        return json.loads(decrypted.decode())
