from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tobacco_trading_system.settings')

app = Celery('tobacco_trading_system')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# Periodic tasks
from celery.schedules import crontab

app.conf.beat_schedule = {
    'update-daily-prices': {
        'task': 'timb_dashboard.tasks.update_daily_prices',
        'schedule': crontab(hour=8, minute=0),  # 8:00 AM daily
    },
    'detect-side-buying': {
        'task': 'ai_models.tasks.detect_side_buying_patterns',
        'schedule': crontab(hour='*/6'),  # Every 6 hours
    },
    'generate-daily-reports': {
        'task': 'timb_dashboard.tasks.generate_daily_reports',
        'schedule': crontab(hour=18, minute=0),  # 6:00 PM daily
    },
    'cleanup-old-data': {
        'task': 'utils.tasks.cleanup_old_data',
        'schedule': crontab(hour=2, minute=0, day_of_week=1),  # 2:00 AM every Monday
    },
}

app.conf.timezone = 'Africa/Harare'

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')