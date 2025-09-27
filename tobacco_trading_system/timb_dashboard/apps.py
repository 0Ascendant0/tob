from django.apps import AppConfig


class TimbDashboardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'timb_dashboard'
    verbose_name = 'TIMB Dashboard'
    
    def ready(self):
        import timb_dashboard.signals