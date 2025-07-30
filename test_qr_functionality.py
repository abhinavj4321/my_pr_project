#!/usr/bin/env python
"""
Test script to verify QR code functionality
"""
import os
import sys
import django

# Setup Django environment
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'student_management_system.settings')
django.setup()

from student_management_app.models import AttendanceQRCode, Subjects, SessionYearModel
from django.utils import timezone
import datetime

def test_qr_functionality():
    print("=== QR Code Functionality Test ===\n")
    
    # 1. Check database state
    print("1. Database State:")
    subjects = Subjects.objects.all()
    session_years = SessionYearModel.objects.all()
    qr_codes = AttendanceQRCode.objects.all()
    active_qr_codes = AttendanceQRCode.objects.filter(is_active=True, expiry_time__gte=timezone.now())
    
    print(f"   - Subjects: {subjects.count()}")
    print(f"   - Session Years: {session_years.count()}")
    print(f"   - Total QR Codes: {qr_codes.count()}")
    print(f"   - Active QR Codes: {active_qr_codes.count()}")
    
    # 2. Show active QR codes
    if active_qr_codes.exists():
        print("\n2. Active QR Codes:")
        for qr in active_qr_codes:
            print(f"   - Token: {qr.token[:20]}...")
            print(f"     Subject: {qr.subject.subject_name}")
            print(f"     Expires: {qr.expiry_time}")
            print(f"     Location Required: {bool(qr.teacher_latitude and qr.teacher_longitude)}")
            if qr.teacher_latitude and qr.teacher_longitude:
                print(f"     Teacher Location: ({qr.teacher_latitude}, {qr.teacher_longitude})")
                print(f"     Allowed Radius: {qr.allowed_radius} meters")
    else:
        print("\n2. No active QR codes found")
    
    # 3. Check expired QR codes
    expired_qr_codes = AttendanceQRCode.objects.filter(is_active=True, expiry_time__lt=timezone.now())
    print(f"\n3. Expired QR Codes: {expired_qr_codes.count()}")
    
    # 4. Test QR code generation data
    print("\n4. QR Generation Requirements:")
    if subjects.exists() and session_years.exists():
        print("   ✅ Can generate QR codes (subjects and session years available)")
        subject = subjects.first()
        session_year = session_years.first()
        print(f"   - Sample Subject: {subject.subject_name} (ID: {subject.id})")
        print(f"   - Sample Session: {session_year.session_start_year}-{session_year.session_end_year} (ID: {session_year.id})")
    else:
        print("   ❌ Cannot generate QR codes (missing subjects or session years)")
    
    # 5. Check URL patterns
    print("\n5. URL Configuration:")
    try:
        from django.urls import reverse
        qr_gen_url = reverse('staff_generate_qr')
        qr_scan_url = reverse('student_scan_qr')
        qr_process_url = reverse('student_process_qr_scan')
        print(f"   ✅ QR Generation URL: {qr_gen_url}")
        print(f"   ✅ QR Scan URL: {qr_scan_url}")
        print(f"   ✅ QR Process URL: {qr_process_url}")
    except Exception as e:
        print(f"   ❌ URL configuration error: {e}")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_qr_functionality()
