import os
from pathlib import Path
from django.core.management.utils import get_random_secret_key
import secrets

# Try to load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv not installed, that's fine
    pass

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', get_random_secret_key())

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'

# Encryption key
ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY', secrets.token_urlsafe(32))

ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '0.0.0.0',
    '.timb.co.zw',  # Production domain
    os.environ.get('DOMAIN_NAME', ''),
]

# Remove empty strings from ALLOWED_HOSTS
ALLOWED_HOSTS = [host for host in ALLOWED_HOSTS if host]

# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
]

THIRD_PARTY_APPS = [
    'channels',
    'corsheaders',
    'rest_framework',
    'django_extensions',
    'crispy_forms',
    'crispy_bootstrap5',
    'mathfilters',
]

LOCAL_APPS = [
    'authentication',
    'timb_dashboard',
    'merchant_app',
    'ai_models',
    'realtime_data',
    'utils',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# Custom User Model
AUTH_USER_MODEL = 'authentication.User'

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'tobacco_trading_system.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'utils.context_processors.global_context',
            ],
        },
    },
]

# WSGI and ASGI applications
WSGI_APPLICATION = 'tobacco_trading_system.wsgi.application'
ASGI_APPLICATION = 'tobacco_trading_system.asgi.application'

# Database configuration
if os.environ.get('DATABASE_URL'):
    # Production database (PostgreSQL)
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.parse(os.environ.get('DATABASE_URL'))
    }
else:
    # Development database (SQLite)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# QR Token database (separate for security)
DATABASES['qr_tokens'] = {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': BASE_DIR / 'qr_tokens.sqlite3',
}

# Database routing
DATABASE_ROUTERS = ['utils.db_router.QRTokenRouter']

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Harare'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# File upload settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024   # 10MB
FILE_UPLOAD_PERMISSIONS = 0o644

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Authentication settings
LOGIN_URL = '/auth/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/auth/login/'

SESSION_COOKIE_AGE = 86400  # 24 hours
SESSION_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

CSRF_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'

# Security settings
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_SSL_REDIRECT = True
    X_FRAME_OPTIONS = 'DENY'

# Channels Configuration (WebSockets)
if os.environ.get('REDIS_URL'):
    # Production Redis
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels_redis.core.RedisChannelLayer',
            'CONFIG': {
                "hosts": [os.environ.get('REDIS_URL')],
            },
        },
    }
else:
    # Development - Try Redis, fallback to in-memory
    try:
        CHANNEL_LAYERS = {
            'default': {
                'BACKEND': 'channels_redis.core.RedisChannelLayer',
                'CONFIG': {
                    "hosts": [('127.0.0.1', 6379)],
                },
            },
        }
    except:
        CHANNEL_LAYERS = {
            'default': {
                'BACKEND': 'channels.layers.InMemoryChannelLayer'
            }
        }

# Celery Configuration (Background Tasks)
if os.environ.get('REDIS_URL'):
    CELERY_BROKER_URL = os.environ.get('REDIS_URL')
    CELERY_RESULT_BACKEND = os.environ.get('REDIS_URL')
else:
    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

# REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# CORS Configuration
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://timb.co.zw",
]

CORS_ALLOW_CREDENTIALS = True

# Crispy Forms Configuration
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Cache configuration
if os.environ.get('REDIS_URL'):
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': os.environ.get('REDIS_URL'),
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            }
        }
    }
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'timb-cache',
        }
    }

# TIMB System Specific Settings
TIMB_SETTINGS = {
    # Real-time data settings
    'REALTIME_PRICE_UPDATE_INTERVAL': 30,  # seconds
    'FRAUD_DETECTION_THRESHOLD': 0.6,
    'SIDE_BUYING_DETECTION_THRESHOLD': 0.5,
    
    # Trading limits
    'MAX_TRANSACTION_AMOUNT': 1000000,  # USD
    'MIN_TRANSACTION_AMOUNT': 10,       # USD
    'MAX_DAILY_TRANSACTIONS_PER_MERCHANT': 100,
    
    # File upload limits
    'MAX_LOGO_SIZE': 2 * 1024 * 1024,    # 2MB
    'MAX_BANNER_SIZE': 5 * 1024 * 1024,   # 5MB
    'MAX_DOCUMENT_SIZE': 10 * 1024 * 1024, # 10MB
    
    # AI Model settings
    'AI_MODELS_DIR': BASE_DIR / 'models',
    'RETRAIN_MODELS_INTERVAL': 7,  # days
    'MIN_TRAINING_SAMPLES': 1000,
    
    # QR Code settings
    'QR_CODE_EXPIRY_MINUTES': 30,
    'QR_CODE_MAX_USES': 10,
    
    # Encryption settings
    'ENCRYPTION_KEY_ROTATION_DAYS': 90,
    'DATA_RETENTION_DAYS': 2555,  # 7 years
}

# Create directories
for directory in [TIMB_SETTINGS['AI_MODELS_DIR']]:
    directory.mkdir(exist_ok=True)

# Email configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True').lower() == 'true'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'TIMB Trading System <noreply@timb.co.zw>')

# Logging configuration
LOGS_DIR = BASE_DIR / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_DIR / 'django.log',
            'maxBytes': 1024*1024*5,  # 5MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'security_file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_DIR / 'security.log',
            'maxBytes': 1024*1024*5,  # 5MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.security': {
            'handlers': ['security_file'],
            'level': 'WARNING',
            'propagate': False,
        },
        'tobacco_trading_system': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'ai_models': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# Development-specific settings
if DEBUG:
    # Email backend for development
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

    # Allow all origins for CORS in development
    CORS_ALLOW_ALL_ORIGINS = True

# Production-specific settings
else:
    # Security headers
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    USE_TZ = True
    
    # Compress static files
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
    
    # Admin security
    ADMIN_URL = os.environ.get('ADMIN_URL', 'admin/')

# Performance settings
if not DEBUG:
    # Database connection pooling
    DATABASES['default'].update({
        'CONN_MAX_AGE': 60,
        'OPTIONS': {
            'MAX_CONNS': 20,
            'OPTIONS': {
                'autocommit': True,
            }
        }
    })

# Monitoring and Error Tracking (Optional - Sentry)
SENTRY_DSN = os.environ.get('SENTRY_DSN')
if SENTRY_DSN and not DEBUG:
    try:
        import sentry_sdk
        from sentry_sdk.integrations.django import DjangoIntegration
        from sentry_sdk.integrations.celery import CeleryIntegration
        
        sentry_sdk.init(
            dsn=SENTRY_DSN,
            integrations=[
                DjangoIntegration(auto_enabling=True),
                CeleryIntegration(auto_enabling=True),
            ],
            traces_sample_rate=0.1,
            send_default_pii=True
        )
    except ImportError:
        pass

# Environment-specific imports
try:
    if DEBUG:
        from .local_settings import *
    else:
        from .production_settings import *
except ImportError:
    pass