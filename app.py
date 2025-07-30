#!/usr/bin/env python
"""
Simple app.py file to help Render detect our Django application correctly.
This file imports the Django WSGI application and makes it available as 'application'.
"""

import os
import sys
from pathlib import Path

# Add the project directory to Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'student_management_system.settings_production')

# Import Django WSGI application
try:
    from student_management_system.wsgi import application
except ImportError as e:
    print(f"Error importing Django WSGI application: {e}")
    # Fallback to development settings if production fails
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'student_management_system.settings')
    from student_management_system.wsgi import application

# Make the application available for gunicorn
app = application

if __name__ == "__main__":
    # This allows running the app directly for testing
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
