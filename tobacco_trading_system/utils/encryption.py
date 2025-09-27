from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from django.conf import settings
import base64
import json
import os

class EncryptionManager:
    """Enhanced encryption manager for sensitive data"""
    
    def __init__(self):
        self.key = self._get_or_create_key()
        self.cipher = Fernet(self.key)
    
    def _get_or_create_key(self):
        """Get or create encryption key"""
        # Check if encryption key is set in settings
        if hasattr(settings, 'ENCRYPTION_KEY') and settings.ENCRYPTION_KEY:
            try:
                # Verify the key format
                key = settings.ENCRYPTION_KEY.encode() if isinstance(settings.ENCRYPTION_KEY, str) else settings.ENCRYPTION_KEY
                # Test if it's a valid Fernet key
                Fernet(key)
                return key
            except:
                pass
        
        # Generate a proper Fernet key from SECRET_KEY
        password = settings.SECRET_KEY.encode()
        salt = b'timb_tobacco_2024_salt_fixed_length'  # Fixed 32-byte salt
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key
    
    def encrypt_data(self, data):
        """Encrypt data (dict, string, or other JSON-serializable data)"""
        try:
            if isinstance(data, (dict, list)):
                data_str = json.dumps(data)
            else:
                data_str = str(data)
            
            encrypted = self.cipher.encrypt(data_str.encode())
            return base64.urlsafe_b64encode(encrypted).decode()
        except Exception as e:
            raise ValueError(f"Encryption failed: {str(e)}")
    
    def decrypt_data(self, encrypted_data):
        """Decrypt data and return original format"""
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted = self.cipher.decrypt(encrypted_bytes)
            data_str = decrypted.decode()
            
            # Try to parse as JSON first
            try:
                return json.loads(data_str)
            except json.JSONDecodeError:
                return data_str
        except Exception as e:
            raise ValueError(f"Decryption failed: {str(e)}")
    
    def encrypt_file(self, file_path):
        """Encrypt a file"""
        try:
            with open(file_path, 'rb') as file:
                file_data = file.read()
            
            encrypted_data = self.cipher.encrypt(file_data)
            
            with open(f"{file_path}.encrypted", 'wb') as encrypted_file:
                encrypted_file.write(encrypted_data)
            
            return f"{file_path}.encrypted"
        except Exception as e:
            raise ValueError(f"File encryption failed: {str(e)}")
    
    def decrypt_file(self, encrypted_file_path, output_path):
        """Decrypt a file"""
        try:
            with open(encrypted_file_path, 'rb') as encrypted_file:
                encrypted_data = encrypted_file.read()
            
            decrypted_data = self.cipher.decrypt(encrypted_data)
            
            with open(output_path, 'wb') as output_file:
                output_file.write(decrypted_data)
            
            return output_path
        except Exception as e:
            raise ValueError(f"File decryption failed: {str(e)}")

# Global encryption instance
encryption = EncryptionManager()