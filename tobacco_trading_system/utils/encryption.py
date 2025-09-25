import base64
import json
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from django.conf import settings
import os

class DataEncryption:
    def __init__(self):
        # Generate key from settings
        password = settings.ENCRYPTION_KEY.encode()
        salt = b'tobacco_trading_salt'  # In production, use a random salt
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        self.cipher_suite = Fernet(key)
    
    def encrypt_data(self, data):
        """Encrypt any data (string, dict, list)"""
        if isinstance(data, (dict, list)):
            data = json.dumps(data)
        elif not isinstance(data, str):
            data = str(data)
        
        encrypted_data = self.cipher_suite.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted_data).decode()
    
    def decrypt_data(self, encrypted_data):
        """Decrypt data back to original format"""
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_bytes = self.cipher_suite.decrypt(encrypted_bytes)
            decrypted_str = decrypted_bytes.decode()
            
            # Try to parse as JSON
            try:
                return json.loads(decrypted_str)
            except json.JSONDecodeError:
                return decrypted_str
        except Exception as e:
            raise ValueError(f"Failed to decrypt data: {str(e)}")

# Global encryption instance
encryption = DataEncryption()