#!/usr/bin/env python
"""
Production Database Setup Script
This script sets up the database with default data for production deployment.
"""

import os
import django
from django.core.management import execute_from_command_line

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'student_management_system.settings')
django.setup()

from student_management_app.models import CustomUser, AdminHOD, SessionYearModel
from django.contrib.auth.hashers import make_password

def setup_database():
    """Set up the database with default data"""
    
    print("🔄 Setting up production database...")
    
    # Run migrations
    print("📦 Running migrations...")
    execute_from_command_line(['manage.py', 'migrate'])
    
    # Check if admin already exists
    if CustomUser.objects.filter(username='admin').exists():
        print("✅ Admin user already exists")
        return
    
    # Create admin user
    print("👤 Creating admin user...")
    admin_user = CustomUser.objects.create(
        username="admin",
        email="admin@example.com",
        first_name="System",
        last_name="Administrator",
        user_type=1,
        password=make_password("admin123")
    )
    
    # Create AdminHOD instance
    admin_hod = AdminHOD.objects.create(admin=admin_user)
    
    # Create default session year
    if not SessionYearModel.objects.exists():
        print("📅 Creating default session year...")
        session_year = SessionYearModel.objects.create(
            session_start_year="2024-01-01",
            session_end_year="2024-12-31"
        )
    
    print("✅ Database setup completed successfully!")
    print("🔐 Admin credentials:")
    print("   Username: admin")
    print("   Password: admin123")

if __name__ == "__main__":
    setup_database()
