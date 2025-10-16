import os
import sys
import django

# Ensure project root is on sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tobacco_trading_system.tobacco_trading_system.settings')

try:
    django.setup()
    from django.template import engines
    eng = engines['django']
    eng.engine.get_template('merchant_app/dashboard.html')
    print('Template loaded successfully')
except Exception as e:
    import traceback
    print('ERROR:', type(e).__name__)
    traceback.print_exc()
