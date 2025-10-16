import os
import django
from django.test import Client

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tobacco_trading_system.settings')
django.setup()

client = Client()
# Use the superuser/timb staff credentials or anonymous; we'll try anonymous and expect redirect to login
resp = client.get('/timb/merchants/')
print('status_code:', resp.status_code)
# Print a small snippet of content or error
content = resp.content.decode('utf-8', errors='replace')
print('content_snippet:', content[:500])
