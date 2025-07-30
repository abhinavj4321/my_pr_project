import os
import dj_database_url
from .settings import *

# SECURITY WARNING: don't run with debug turned on in production!
# Temporarily enable DEBUG to see the actual error
DEBUG = True

# For now, use SQLite to get the app working, then we can migrate to PostgreSQL later
# Parse database connection url
DATABASE_URL = os.environ.get('DATABASE_URL')
print(f"DATABASE_URL: {DATABASE_URL}")  # Debug

if DATABASE_URL and 'postgres' in DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.config(default=DATABASE_URL, conn_max_age=600)
    }
    print(f"Using PostgreSQL database: {DATABASES['default']['ENGINE']}")  # Debug
else:
    # Use SQLite for now since PostgreSQL has compatibility issues with Python 3.13
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }
    print("Using SQLite database for compatibility")  # Debug

# Use environment variable for secret key
SECRET_KEY = os.environ.get('SECRET_KEY', SECRET_KEY)

# Allow all hosts temporarily for debugging
ALLOWED_HOSTS = ['*']

# Enable WhiteNoise for static files
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')

# Static files configuration
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
# Temporarily use simpler static files storage
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# Keep the existing STATICFILES_DIRS
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Media files configuration
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Security settings - temporarily disabled for debugging
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_BROWSER_XSS_FILTER = True
