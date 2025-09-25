import qrcode
import uuid
from datetime import datetime, timedelta
from io import BytesIO
import base64
from django.utils import timezone
from utils.encryption import encryption

class QRCodeManager:
    def __init__(self):
        self.encryption = encryption
    
    def generate_access_token(self, data, expiry_minutes=30):
        """Generate encrypted QR code with access token"""
        # Create unique token
        token = str(uuid.uuid4())
        
        # Prepare token data
        token_data = {
            'token': token,
            'data_ref': str(uuid.uuid4()),  # Reference to actual data
            'created_at': timezone.now().isoformat(),
            'expires_at': (timezone.now() + timedelta(minutes=expiry_minutes)).isoformat(),
            'access_count': 0
        }
        
        # Encrypt the actual data
        encrypted_data = self.encryption.encrypt_data(data)
        
        # Generate QR code for token
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        
        # Encrypt token data for QR code
        qr_data = self.encryption.encrypt_data(token_data)
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        # Create QR code image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        qr_code_base64 = base64.b64encode(buffered.getvalue()).decode()
        
        return {
            'token': token,
            'data_ref': token_data['data_ref'],
            'encrypted_data': encrypted_data,
            'qr_code': qr_code_base64,
            'expires_at': token_data['expires_at']
        }
    
    def verify_and_get_data(self, qr_token_data, increment_access=True):
        """Verify QR token and return decrypted data"""
        try:
            # Decrypt QR token
            token_info = self.encryption.decrypt_data(qr_token_data)
            
            # Check expiry
            expires_at = datetime.fromisoformat(token_info['expires_at'].replace('Z', '+00:00'))
            if timezone.now() > expires_at:
                raise ValueError("QR code has expired")
            
            if increment_access:
                token_info['access_count'] += 1
            
            return token_info
        except Exception as e:
            raise ValueError(f"Invalid QR code: {str(e)}")

qr_manager = QRCodeManager()