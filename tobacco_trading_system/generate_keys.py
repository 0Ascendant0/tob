import secrets
from django.core.management.utils import get_random_secret_key

# Generate secure keys
secret_key = get_random_secret_key()
encryption_key = secrets.token_urlsafe(32)

print("Add these to your .env file:")
print(f"SECRET_KEY={secret_key}")
print(f"ENCRYPTION_KEY={encryption_key}")