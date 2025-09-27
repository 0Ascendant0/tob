from django.conf import settings
from django.utils import timezone

def global_context(request):
    """Global context processor for TIMB system"""
    return {
        'TIMB_SETTINGS': getattr(settings, 'TIMB_SETTINGS', {}),
        'current_time': timezone.now(),
        'system_name': 'TIMB Trading System',
        'system_version': '1.0.0',
    }