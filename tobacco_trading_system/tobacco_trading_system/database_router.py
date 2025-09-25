class DatabaseRouter:
    """
    A router to control all database operations on models for different apps
    """
    
    route_app_labels = {'qr_tokens', 'merchant_app', 'timb_dashboard', 'ai_models', 'authentication', 'realtime_data'}

    def db_for_read(self, model, **hints):
        """Suggest the database that should be read from for objects of type model."""
        if model._meta.app_label == 'qr_tokens':
            return 'qr_tokens'
        return 'default'

    def db_for_write(self, model, **hints):
        """Suggest the database that should be written to for objects of type model."""
        if model._meta.app_label == 'qr_tokens':
            return 'qr_tokens'
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        """Allow relations if models are in the same app."""
        db_set = {'default', 'qr_tokens'}
        if obj1._state.db in db_set and obj2._state.db in db_set:
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """Ensure that certain apps' models get created on the right database."""
        if app_label == 'qr_tokens':
            return db == 'qr_tokens'
        elif db == 'qr_tokens':
            return False
        return db == 'default'