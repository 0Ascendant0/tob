class QRTokenRouter:
    """
    A router to control database operations for QR token models
    """
    
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'qr_tokens':
            return 'qr_tokens'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'qr_tokens':
            return 'qr_tokens'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        # Allow relations within the same database
        db_set = {'default', 'qr_tokens'}
        if obj1._state.db in db_set and obj2._state.db in db_set:
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == 'qr_tokens':
            return db == 'qr_tokens'
        elif db == 'qr_tokens':
            return False
        return db == 'default'