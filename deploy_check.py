#!/usr/bin/env python3
"""
Deployment Readiness Checker for Student Attendance System
"""
import os
import sys

def check_file_exists(filepath, description):
    """Check if a file exists and print status"""
    if os.path.exists(filepath):
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description}: {filepath} - MISSING")
        return False

def check_deployment_readiness():
    """Check if the project is ready for deployment"""
    print("🚀 DEPLOYMENT READINESS CHECK")
    print("=" * 50)
    
    all_good = True
    
    # Check essential files
    files_to_check = [
        ("requirements.txt", "Dependencies file"),
        ("manage.py", "Django management script"),
        ("render.yaml", "Render deployment config"),
        ("build.sh", "Build script"),
        ("start.sh", "Start script"),
        ("student_management_system/settings_production.py", "Production settings"),
        ("student_management_system/wsgi.py", "WSGI application"),
    ]
    
    for filepath, description in files_to_check:
        if not check_file_exists(filepath, description):
            all_good = False
    
    print("\n📦 CHECKING REQUIREMENTS...")
    
    # Check requirements.txt content
    try:
        with open("requirements.txt", "r") as f:
            content = f.read()
            required_packages = ["Django", "gunicorn", "whitenoise", "psycopg2-binary", "dj-database-url"]
            for package in required_packages:
                if package in content:
                    print(f"✅ {package} found in requirements.txt")
                else:
                    print(f"❌ {package} missing from requirements.txt")
                    all_good = False
    except FileNotFoundError:
        print("❌ requirements.txt not found")
        all_good = False
    
    print("\n🔧 CHECKING CONFIGURATION...")
    
    # Check if production settings exist
    try:
        import student_management_system.settings_production
        print("✅ Production settings can be imported")
    except ImportError as e:
        print(f"❌ Production settings import failed: {e}")
        all_good = False
    
    print("\n📊 DEPLOYMENT SUMMARY")
    print("=" * 50)
    
    if all_good:
        print("🎉 YOUR PROJECT IS READY FOR DEPLOYMENT!")
        print("\n📋 NEXT STEPS:")
        print("1. Push your code to GitHub:")
        print("   git add .")
        print("   git commit -m 'Ready for deployment'")
        print("   git push origin main")
        print("\n2. Deploy on Render:")
        print("   - Go to https://render.com")
        print("   - Sign up and connect GitHub")
        print("   - Create new Web Service from your repo")
        print("   - Render will auto-detect render.yaml")
        print("   - Click Deploy!")
        print("\n3. Alternative platforms:")
        print("   - Railway: https://railway.app")
        print("   - PythonAnywhere: https://pythonanywhere.com")
    else:
        print("⚠️  SOME ISSUES FOUND - Please fix them before deploying")
    
    return all_good

if __name__ == "__main__":
    check_deployment_readiness()
