import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
from qrcode.image.styles.colormasks import SquareGradiantColorMask
import io
import base64
import secrets
import uuid
from datetime import datetime, timedelta
from django.utils import timezone
from .encryption import encryption

class QRCodeManager:
    """Enhanced QR code generation and management"""
    
    def __init__(self):
        self.version = 1
        self.error_correction = qrcode.constants.ERROR_CORRECT_L
        self.box_size = 10
        self.border = 4
    
    def generate_qr_code(self, data, style='default'):
        """Generate QR code with optional styling"""
        qr = qrcode.QRCode(
            version=self.version,
            error_correction=self.error_correction,
            box_size=self.box_size,
            border=self.border,
        )
        
        qr.add_data(data)
        qr.make(fit=True)
        
        if style == 'styled':
            img = qr.make_image(
                image_factory=StyledPilImage,
                module_drawer=RoundedModuleDrawer(),
                color_mask=SquareGradiantColorMask(
                    back_color=(255, 255, 255),
                    center_color=(5, 92, 222),
                    edge_color=(93, 92, 222)
                )
            )
        else:
            img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()
        return f"data:image/png;base64,{qr_code_base64}"
    
    def generate_access_token(self, data, expiry_minutes=60):
        """Generate secure access token with QR code"""
        # Generate unique token and reference
        token = secrets.token_urlsafe(32)
        data_ref = str(uuid.uuid4())
        
        # Add metadata
        token_data = {
            'token': token,
            'data_ref': data_ref,
            'created_at': timezone.now().isoformat(),
            'expires_at': (timezone.now() + timedelta(minutes=expiry_minutes)).isoformat(),
            'data': data
        }
        
        # Encrypt the data
        encrypted_data = encryption.encrypt_data(token_data)
        
        # Generate QR code
        qr_url = f"https://timb.gov.zw/qr/{token}/"
        qr_code = self.generate_qr_code(qr_url, style='styled')
        
        return {
            'token': token,
            'data_ref': data_ref,
            'qr_code': qr_code,
            'encrypted_data': encrypted_data,
            'expires_at': (timezone.now() + timedelta(minutes=expiry_minutes)).isoformat()
        }
    
    def generate_inventory_qr(self, inventory_data):
        """Generate QR code for inventory sharing"""
        return self.generate_access_token({
            'type': 'inventory',
            'merchant': inventory_data.get('merchant_name'),
            'items': inventory_data.get('items', []),
            'total_value': inventory_data.get('total_value', 0),
            'generated_at': timezone.now().isoformat()
        }, expiry_minutes=120)
    
    def generate_transaction_qr(self, transaction_data):
        """Generate QR code for transaction verification"""
        return self.generate_access_token({
            'type': 'transaction',
            'transaction_id': transaction_data.get('transaction_id'),
            'parties': {
                'buyer': transaction_data.get('buyer'),
                'seller': transaction_data.get('seller')
            },
            'details': {
                'grade': transaction_data.get('grade'),
                'quantity': transaction_data.get('quantity'),
                'price': transaction_data.get('price'),
                'total': transaction_data.get('total')
            },
            'timestamp': transaction_data.get('timestamp')
        }, expiry_minutes=1440)  # 24 hours
    
    def generate_report_qr(self, report_data):
        """Generate QR code for report sharing"""
        return self.generate_access_token({
            'type': 'report',
            'report_title': report_data.get('title'),
            'generated_by': report_data.get('generated_by'),
            'data': report_data.get('data'),
            'summary': report_data.get('summary')
        }, expiry_minutes=180)  # 3 hours

# Global QR manager instance
qr_manager = QRCodeManager()