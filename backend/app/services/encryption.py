"""
Encryption Service
Encrypt/decrypt sensitive data like database connection strings.
"""

from cryptography.fernet import Fernet

from app.core.config import settings
from app.core.logging import logger


class EncryptionService:
    """Service for encrypting and decrypting sensitive data."""
    
    def __init__(self):
        # In production, load from environment variable
        # For now, use the SECRET_KEY
        key = settings.secret_key.encode()[:32]  # Fernet needs 32 bytes
        # Pad to 32 bytes if shorter
        key = key + b'0' * (32 - len(key))
        # Base64 encode for Fernet
        import base64
        self.fernet = Fernet(base64.urlsafe_b64encode(key))
    
    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt plaintext string.
        
        Args:
            plaintext: String to encrypt
            
        Returns:
            Encrypted string (base64 encoded)
        """
        try:
            encrypted_bytes = self.fernet.encrypt(plaintext.encode())
            return encrypted_bytes.decode()
        except Exception as e:
            logger.error("encryption.failed", error=str(e))
            raise
    
    def decrypt(self, ciphertext: str) -> str:
        """
        Decrypt ciphertext string.
        
        Args:
            ciphertext: Encrypted string (base64 encoded)
            
        Returns:
            Decrypted plaintext string
        """
        try:
            decrypted_bytes = self.fernet.decrypt(ciphertext.encode())
            return decrypted_bytes.decode()
        except Exception as e:
            logger.error("encryption.decrypt_failed", error=str(e))
            raise


# Global instance
encryption_service = EncryptionService()














